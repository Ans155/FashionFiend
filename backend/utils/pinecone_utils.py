"""Contains the logic to interact with the Pinecone vector database."""

import os
import typing as t
from pinecone import Pinecone, ServerlessSpec

from common import logger
from common.constants import _PINECONE_API_KEY

log = logger.create_logger()

_DEFAULT_DIMENSION = 384
_DEFAULT_METRIC = "cosine"


def initialize_index(
    index_name: str, dimension: int = _DEFAULT_DIMENSION, metric: str = _DEFAULT_METRIC
) -> Pinecone.Index:
    """Creates a new index in Pinecone."""
    pc = Pinecone(api_key=_PINECONE_API_KEY, environment="us-east-1-aws")
    try:
        index = pc.Index(index_name)
        log.info(f"Connected to existing Pinecone index: {index_name}")
    except Exception as e:
        log.warning(f"Error in initializing Pinecone index: {index_name} - {e}")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        index = pc.Index(index_name)
        log.warning(f"Successfully created Pinecone index: {index_name}")
    return index


def query_index(index: Pinecone.Index, query: str, top_k: int = 1) -> list:
    """Queries the index."""
    return index.query(vector=query, top_k=top_k, include_metadata=True)


def fetch_matching_vectors_metadata(
    index: Pinecone.Index,
    query_embedding: list[float],
    top_k: int = 1,
    similarity_threshold: float = 0.9,
    apply_threshold: bool = True,
    filters: t.Optional[dict[str, t.Any]] = None,
) -> list[dict]:
    """Fetches the matching metadata."""
    similar_queries = index.query(
        vector=query_embedding, top_k=top_k, include_metadata=True, filter=filters
    )
    similar_vectors_metadata = [
        {
            "id": match["id"],
            "score": match["score"],
            "metadata": match.get("metadata", dict()),
        }
        for match in similar_queries["matches"]
    ]

    if apply_threshold:
        selected_vectors_metadata = [
            match
            for match in similar_vectors_metadata
            if match["score"] >= similarity_threshold
        ]
        return selected_vectors_metadata
    return similar_vectors_metadata


def upsert_single_vector(
    index: Pinecone.Index,
    vector_id: str,
    query_embedding: list[float],
    metadata: dict[str, str],
) -> None:
    """Upserts single vector to pinecone index."""
    try:
        index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": query_embedding,
                    "metadata": metadata,
                }
            ]
        )
    except Exception as e:
        log.error(f"Error upserting vector to pinecone metadata: {metadata} - {e}")


def upsert_multiple_vector(
    index: Pinecone.Index,
    vectors: list[dict[str, t.Any]],
) -> None:
    """Upserts multiple vectors to pinecone index."""
    try:
        response = index.upsert(vectors=vectors)
        log.info(f"Ingested multiple vectors with response: `{response}`")
    except Exception as e:
        log.error(f"Error upserting multiple vectors to pinecone - {e}")


# def fetch_all_ids(index: Pinecone.Index, namespace: str = "") -> list[str]:
#     """Fetches all the ingested ids for an index."""
#     try:
#         index_stats = index.describe_index_stats()
#         namespaces_metadata = index_stats["namespaces"]
#         if (
#             index_stats["total_vector_count"] > 0
#             and namespace in namespaces_metadata.keys()
#         ):
#             vector_count = namespaces_metadata[namespace]["vector_count"]
#             dimension = index_stats["dimension"]
#             all_vectors = index.query(
#                 vector=[0] * dimension, top_k=vector_count, include_metadata=False
#             )
#             ids = [vector["id"] for vector in all_vectors["matches"]]
#             log.info(f"Found {len(ids)} in index.")
#             return ids
#     except Exception as e:
#         log.error(f"Error in reading all vector ids: `{e}`")
#     return []
import json
import logging
from pinecone import Index

# Initialize logger
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def fetch_all_ids(index: Index, namespace: str = "") -> list[str]:
    """
    Fetches all the ingested IDs for an index and saves them to a JSON file.
    
    Args:
        index (Index): Pinecone index object.
        namespace (str): Namespace to filter vectors by.
    
    Returns:
        list[str]: List of IDs.
    """
    try:
        # index_stats = index.describe_index_stats()
        # namespaces_metadata = "default"
        
        # vector_count = namespaces_metadata[namespace].get("vector_count", 0)
            # dimension = index_stats["dimension"]
        dimension = 384
        all_vectors = index.query(
            vector=[0] * dimension, top_k=vector_count, include_metadata=True
        )
        ids = [vector["id"] for vector in all_vectors.get("matches", [])]
            
        log.info(f"Found {len(ids)} IDs in index.")

            # Save IDs to a JSON file
        json_file_name = f"vector_ids_default.json"
        with open(json_file_name, "w") as json_file:
            json.dump(ids, json_file, indent=4)
        log.info(f"Exported IDs to `{json_file_name}`.")
            
        return ids
    except Exception as e:
        log.error(f"Error in reading all vector IDs: `{e}`")
    return []



def delete_ids(index: Pinecone.Index, vector_ids: list[str], namespace: str = ""):
    """Deletes the vector ids from specific index."""
    index.delete(ids=vector_ids, namespace=namespace)