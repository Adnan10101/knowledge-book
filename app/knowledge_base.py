import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import json

def load_knowledge_base_csv(csv_path: str) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Load knowledge base from CSV file.
    
    Args:
        csv_path (str): Path to the CSV file.
    
    Returns:
        Tuple of (DataFrame, vectors as 2D numpy array)
    """
    print(f"Loading knowledge base from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Convert embedding vectors back to numpy arrays
    vectors = []
    for vector_str in df["embedding_vector"]:
        if isinstance(vector_str, str):
            vector = np.array(json.loads(vector_str))
        else:
            vector = np.array(vector_str)
        vectors.append(vector)
    
    vectors = np.array(vectors)
    print(f"✓ Loaded {len(df)} chunks, vectors shape: {vectors.shape}")
    return df, vectors

def search_similar_chunks(
    query_vector: np.ndarray,
    knowledge_vectors: np.ndarray,
    df: pd.DataFrame,
    top_k: int = 5,
    threshold: float = None
) -> List[Dict]:
    """
    Search for similar chunks using cosine similarity.
    
    Args:
        query_vector (np.ndarray): The query embedding vector.
        knowledge_vectors (np.ndarray): 2D array of all chunk vectors.
        df (pd.DataFrame): DataFrame containing chunk metadata.
        top_k (int): Number of top results to return.
        threshold (float): Optional similarity threshold (0-1).
    
    Returns:
        List[Dict]: Top-k most similar chunks with similarity scores.
    """
    # Calculate cosine similarity
    # Normalize vectors for cosine similarity
    query_norm = query_vector / np.linalg.norm(query_vector)
    knowledge_norms = knowledge_vectors / np.linalg.norm(knowledge_vectors, axis=1, keepdims=True)
    
    # Compute similarities
    similarities = np.dot(knowledge_norms, query_norm)
    
    # Get top-k indices
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    # Build results
    results = []
    for idx in top_indices:
        similarity = float(similarities[idx])
        
        # Apply threshold if specified
        if threshold and similarity < threshold:
            continue
        
        chunk_data = df.iloc[idx].to_dict()
        results.append({
            "similarity": similarity,
            "metadata": chunk_data
        })
    
    return results

def handle_query(
    user_query: str,
    model: SentenceTransformer,
    df: pd.DataFrame,
    knowledge_vectors: np.ndarray,
    top_k: int = 5
) -> List[Dict]:
    """
    Handle a user query by vectorizing and searching the knowledge base.
    
    Args:
        user_query (str): The user's query text.
        model (SentenceTransformer): The embedding model.
        df (pd.DataFrame): Knowledge base DataFrame.
        knowledge_vectors (np.ndarray): Pre-computed chunk vectors.
        top_k (int): Number of results to retrieve.
    
    Returns:
        List[Dict]: Top-k results with metadata and similarity scores.
    """
    # Vectorize the query
    query_vector = model.encode(user_query)
    
    # Search for similar chunks
    results = search_similar_chunks(query_vector, knowledge_vectors, df, top_k=top_k)
    
    return results
