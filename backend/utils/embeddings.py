import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
import json
from tqdm import tqdm
from typing import List, Dict, Any
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

DEFAULT_DIMENSION = 384
DEFAULT_METRIC = 'cosine'

class FashionEmbeddingManager:
    def __init__(self, 
                 mongodb_conn_string: str,
                 db_name: str,
                 collection_name: str,
                 model_name: str = "all-MiniLM-L6-v2",
                 dimension: int = DEFAULT_DIMENSION):
        """
        Initialize the embedding manager with MongoDB and SentenceTransformer.
        
        Args:
            mongodb_conn_string: MongoDB connection string
            db_name: Name of the MongoDB database
            collection_name: Name of the MongoDB collection
            model_name: Name of the sentence transformer model
            dimension: Dimension of the embeddings
        """
        self.model = SentenceTransformer(model_name)
        self.client = MongoClient(mongodb_conn_string)
        self.collection = self.client[db_name][collection_name]
        log.info(f"Connected to MongoDB collection: {db_name}.{collection_name}")

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare the fashion data."""
        df['baseColour'].fillna('Not Specified', inplace=True)
        df['season'].fillna('All Season', inplace=True)
        df['year'].fillna(df['year'].mode()[0], inplace=True)
        df['usage'].fillna('Casual', inplace=True)
        df['productDisplayName'].fillna('Unknown Product', inplace=True)
        return df

    def create_text_representation(self, row: pd.Series) -> str:
        """Create a rich text representation of the fashion item for embedding."""
        return f"""
        Product: {row['productDisplayName']}
        Category: {row['masterCategory']} - {row['subCategory']} - {row['articleType']}
        Style: {row['gender']} {row['usage']} wear in {row['baseColour']} for {row['season']}
        Year: {row['year']}
        """

    def generate_embeddings(self, df: pd.DataFrame, batch_size: int = 100):
        """
        Generate embeddings for the fashion items and upload to MongoDB in batches.
        
        Args:
            df: DataFrame containing fashion items
            batch_size: Number of items to process in each batch
        """
        total_batches = len(df) // batch_size + (1 if len(df) % batch_size != 0 else 0)
        
        for i in tqdm(range(0, len(df), batch_size), 
                     desc="Generating embeddings", 
                     total=total_batches):
            batch_df = df.iloc[i:i+batch_size]
            texts = [self.create_text_representation(row) for _, row in batch_df.iterrows()]
            
            try:
                embeddings = self.model.encode(texts)
                documents = []
                for j, (_, row) in enumerate(batch_df.iterrows()):
                    document = {
                        "_id": str(row['id']),
                        "embedding": embeddings[j].tolist(),
                        "metadata": {
                            "image_id": row['id'],
                            "text": texts[j],
                            "gender": row['gender'],
                            "masterCategory": row['masterCategory'],
                            "subCategory": row['subCategory'],
                            "articleType": row['articleType'],
                            "baseColour": row['baseColour'],
                            "season": row['season'],
                            "year": str(row['year']),
                            "usage": row['usage'],
                            "productDisplayName": row['productDisplayName']
                        }
                    }
                    documents.append(document)
                
                self.collection.insert_many(documents)
                log.info(f"Successfully uploaded batch {i // batch_size + 1}/{total_batches}")
            except Exception as e:
                log.error(f"Error processing batch {i // batch_size + 1}: {e}")
                continue

    def query_similar_items(self, 
                            query_text: str, 
                            n_results: int = 5, 
                            filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Query for similar fashion items using embeddings.
        
        Args:
            query_text: Text to search for
            n_results: Number of results to return
            filter_dict: Metadata filters for the query
        
        Returns:
            List of search results
        """
        try:
            query_embedding = self.model.encode(query_text).tolist()
            pipeline = [
                {
                    "$search": {
                        "knnBeta": {
                            "vector": query_embedding,
                            "path": "embedding",
                            "k": n_results
                        }
                    }
                }
            ]
            if filter_dict:
                pipeline[0]["$search"]["knnBeta"]["filter"] = filter_dict

            results = list(self.collection.aggregate(pipeline))
            return results
        except Exception as e:
            log.error(f"Error querying similar items: {e}")
            return []

def main():
    # Configuration
    mongodb_conn_string = "mongodb+srv://Ansh155:Ansh@cluster0.djguq6t.mongodb.net/?retryWrites=true&w=majority"
    db_name = "search_dbprojectx"
    collection_name = "search_col4525"
    model_name = "all-MiniLM-L6-v2"

    # Load the fashion dataset
    log.info("Loading fashion dataset...")
    df = pd.read_csv('/Users/spurge/Desktop/recommendation/src/data/styles.csv', on_bad_lines='skip')

    # Initialize the embedding manager
    log.info("Initializing embedding manager...")
    embedding_manager = FashionEmbeddingManager(
        mongodb_conn_string=mongodb_conn_string,
        db_name=db_name,
        collection_name=collection_name,
        model_name=model_name
    )

    # Clean the data
    log.info("Cleaning data...")
    df_cleaned = embedding_manager.clean_data(df)

    # Generate and store embeddings
    log.info("Generating and storing embeddings...")
    embedding_manager.generate_embeddings(df_cleaned)

    # Example query
    log.info("Testing with example query...")
    query = "casual summer dress in blue for women"
    results = embedding_manager.query_similar_items(
        query_text=query,
        n_results=5,
        filter_dict={"gender": "Women"}
    )
    
    if results:
        log.info("Example query results:")
        print(json.dumps(results, indent=2))
    else:
        log.error("No results found for the query")

if __name__ == "__main__":
    main()