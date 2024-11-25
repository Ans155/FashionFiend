from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import boto3
import json
import logging
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import re
from agents.serper import _search_serper
from data.filters import VALID_FILTERS
from prompts.reco_prompt import _RECOMMENDATION_SYSTEM
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware to allow requests from everywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class RecommendationRequest(BaseModel):
    query: str

class ProductInfo(BaseModel):
    name: str
    url: Optional[str]
    category: str
    metadata: Dict[str, Any]

class RecommendationResponse(BaseModel):
    recommendation_text: str
    products: List[ProductInfo]


def init_mongodb(conn_string: str, db_name: str, collection_name: str) -> MongoClient:
    """Initialize MongoDB connection."""
    client = MongoClient(conn_string)
    return client[db_name][collection_name]

def init_bedrock_client(profile_name: Optional[str] = None, region: str = "us-east-1"):
    """Initialize Bedrock client."""
    session = boto3.Session(profile_name=profile_name)
    return session.client(
        service_name='bedrock-runtime',
        region_name=region
    )

def init_embedding_model(model_name: str = 'all-MiniLM-L6-v2') -> SentenceTransformer:
    """Initialize the sentence transformer model."""
    return SentenceTransformer(model_name)

def generate_embedding(model: SentenceTransformer, text: str) -> List[float]:
    """Generate embedding for input text."""
    try:
        embedding = model.encode([text], normalize_embeddings=True)[0]
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise

async def generate_llm_response(
    client,
    prompt: str,
    model_id: str = "anthropic.claude-3-haiku-20240307-v1:0",
    max_tokens: int = 4096,
    temperature: float = 0.0
) -> str:
    """Generate response using Bedrock LLM."""
    try:

        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.8,google_api_key=google_api_key)
        response = model.invoke(prompt)
        print(response)
        response_body = json.loads(response.get('body').read())
        return response_body['content'][0]['text']
    
    except Exception as e:
        logger.error(f"Error generating LLM response: {e}")
        raise

async def rewrite_search_query(client, user_query: str) -> str:
    """Rewrite user query to better match MongoDB metadata structure."""
    prompt = f"""Given this fashion-related query: "{user_query}"

Please rewrite it as a detailed product description that matches these exact metadata categories:

1. Core Categories (use exact terms):
- Master Category: {json.dumps(VALID_FILTERS['masterCategory'])}
- Sub Category: {json.dumps(VALID_FILTERS['subCategory'])}
- Article Type: {json.dumps(VALID_FILTERS['articleType'])}

2. Style Attributes (use exact terms):
- Gender: {json.dumps(VALID_FILTERS['gender'])}
- Usage: {json.dumps(VALID_FILTERS['usage'])}
- Season: {json.dumps(VALID_FILTERS['season'])}
- Base Color: {json.dumps(VALID_FILTERS['baseColour'])}

Guidelines:
- Use exact terms from the provided category lists
- Include as many relevant attributes as can be inferred from the query
- Maintain natural language flow while incorporating these specific terms
- Focus on attributes that will be most useful for vector similarity search

Format the rewritten query as a detailed product description following this pattern:
"Looking for a [Article Type] in the [Master Category] - [Sub Category] category. Ideal for [Gender] [Usage] wear, preferably in [Base Color] color, suitable for [Season] season."

Return only the rewritten description without any explanation."""
    return await generate_llm_response(client, prompt, temperature=0.0)
    

def vector_search(
    collection,
    query_embedding: List[float],
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Perform vector search in MongoDB."""
    try:
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "limit": limit,
                    "numCandidates": limit * 2
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        logger.info(f"Found {len(results)} results from vector search")
        return results
    
    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        raise

def format_search_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for LLM processing."""
    formatted_items = []
    
    for i, result in enumerate(results, 1):
        metadata = result.get('metadata', {})
        formatted_item = f"""
Item {i}:
- Name: {metadata.get('productDisplayName', 'N/A')}
- Category: {metadata.get('masterCategory', 'N/A')} → {metadata.get('subCategory', 'N/A')} → {metadata.get('articleType', 'N/A')}
- Demographics: {metadata.get('gender', 'N/A')}
- Usage: {metadata.get('usage', 'N/A')} wear
- Color: {metadata.get('baseColour', 'N/A')}
- Season: {metadata.get('season', 'N/A')}
- Score: {result.get('score', 0.0):.3f}
"""
        formatted_items.append(formatted_item)
    
    return "\n".join(formatted_items)

async def generate_recommendations(
    client,
    user_query: str,
    search_results: str
) -> str:
    """Generate fashion recommendations using search results and parse the response."""
    
    prompt = _RECOMMENDATION_SYSTEM.format(
        MONGO_RESULTS=search_results,
        USER_QUERY=user_query
    )

    response = await generate_llm_response(client, prompt)
    
    match = re.search(r"<response>(.*?)</response>", response, re.DOTALL)
    if match:
        return match.group(1).strip()  
    else:
        raise ValueError("No content found between <response> tags.")

def extract_product_names(recommendation_text: str) -> List[str]:
    """Extract product names from recommendation text."""
    return re.findall(r'\[(.*?)\]', recommendation_text)

async def process_recommendations(recommendation_text: str, search_results: List[Dict[str, Any]]) -> RecommendationResponse:
    """Process recommendations and fetch product URLs."""
    product_names = extract_product_names(recommendation_text)
    products = []
    

    product_metadata = {
        result['metadata']['productDisplayName']: result['metadata']
        for result in search_results
    }
    
    for product_name in product_names:
        url = _search_serper(product_name)
        metadata = product_metadata.get(product_name, {})
        category = f"{metadata.get('masterCategory', '')} - {metadata.get('subCategory', '')}"
        
        products.append(ProductInfo(
            name=product_name,
            url=url,
            category=category,
            metadata=metadata
        ))
    
    return RecommendationResponse(
        recommendation_text=recommendation_text,
        products=products
    )

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get fashion recommendations with product URLs."""
    try:
        print(request)
        return {
    "recommendation_text": "Hi there! I understand you're looking for a great outfit for the upcoming Diwali festivities. I've got the perfect recommendation for you!\n\nFor your main piece, I suggest the [Global Desi Women Multi Coloured Kurta]. This vibrant, multi-colored kurta is perfect for a Diwali celebration, with its ethnic print and festive vibe. To pair with it, I recommend the [Global Desi Women Solid Red Palazzo Pants]. The solid red color will complement the kurta beautifully and create a cohesive, traditional look.\n\nFor footwear, I think the [Ethnic Wear Embroidered Mojari Flats in Gold] would be a lovely choice. The intricate embroidery and gold tone will add a touch of elegance to your outfit.\n\nTo accessorize, I recommend adding an [Embellished Dupatta in Red and Gold]. The rich colors and embellishments will tie the entire ensemble together and elevate your Diwali look.\n\nI hope this helps you create the perfect outfit for the Diwali festivities! Let me know if you'd like any other recommendations.",
    "products": [
        {
            "name": "Global Desi Women Multi Coloured Kurta",
            "url": "http://www.myntra.com/Kurta-Sets/Global+Desi/Global-Desi-Geometri-Printed-Pure-Cotton-Kurta-with-Palazzos/27615912/buy",
            "category": "Apparel - Topwear",
            "metadata": {
                "image_id": 59062,
                "text": "\n        Product: Global Desi Women Multi Coloured Kurta\n        Category: Apparel - Topwear - Kurtas\n        Style: Women Ethnic wear in Multi for Summer\n        Year: 2012.0\n        ",
                "gender": "Women",
                "masterCategory": "Apparel",
                "subCategory": "Topwear",
                "articleType": "Kurtas",
                "baseColour": "Multi",
                "season": "Summer",
                "year": "2012.0",
                "usage": "Ethnic",
                "productDisplayName": "Global Desi Women Multi Coloured Kurta"
            }
        },
        {
            "name": "Global Desi Women Solid Red Palazzo Pants",
            "url": "http://www.myntra.com/Trousers/Global+Desi/Global-Desi-Women-Navy-Blue-Solid-Mid-Rise-Parallel-Trousers/12550288/buy",
            "category": " - ",
            "metadata": {}
        },
        {
            "name": "Ethnic Wear Embroidered Mojari Flats in Gold",
            "url": "https://www.nrbynidhirathi.in/products/nr-by-nidhi-rathi-women-gold-toned-embellished-leather-ethnic-mojaris-flats-nrhw057an?variant=49583324725541&country=IN&currency=INR&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&srsltid=AfmBOoqRBfQK3ZOnZAWx_fsvWMeOnqtbayBPRatleWRIDlDWyMirdIQHqW8",
            "category": " - ",
            "metadata": {}
        },
        {
            "name": "Embellished Dupatta in Red and Gold",
            "url": "http://www.myntra.com/Dupatta/Dupatta+Bazaar/Dupatta-Bazaar-Red--Gold-Embroidered-Organza-Dupatta-with-Beads-and-Stones-Details/15043244/buy",
            "category": " - ",
            "metadata": {}
        }
    ]}
        collection = init_mongodb(
            conn_string="mongodb+srv://Ansh155:Ansh@cluster0.djguq6t.mongodb.net/?retryWrites=true&w=majority",
            db_name="search_dbprojectx",
            collection_name="search_col4525"
        )
         
        bedrock_client = init_bedrock_client(region="us-east-1")
        embedding_model = init_embedding_model()

        enhanced_query = await rewrite_search_query(bedrock_client, request.query)
        print(enhanced_query)
        query_embedding = generate_embedding(embedding_model, enhanced_query)
        search_results = vector_search(collection, query_embedding)

        if not search_results:
            raise HTTPException(
                status_code=404,
                detail="No matching products found"
            )

        formatted_results = format_search_results(search_results)
        recommendation_text = await generate_recommendations(
            bedrock_client,
            request.query,
            formatted_results
        )

        response = await process_recommendations(recommendation_text, search_results)
        return response

    except Exception as e:
        logger.error(f"Error in recommendation endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)