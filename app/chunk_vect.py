from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from typing import List, Dict
import os

def vectorize_chunks(chunks: List[Dict], model_name: str = "all-MiniLM-L6-v2") -> List[Dict]:
    """
    Vectorizes text chunks using a pre-trained SentenceTransformer model.
    
    Args:
        chunks (List[Dict]): List of chunk dictionaries with 'embedding_text' field.
        model_name (str): Name of the SentenceTransformer model.
    
    Returns:
        List[Dict]: List of dictionaries with vectors and metadata.
    """
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    
    vectorized_chunks = []
    
    print(f"Vectorizing {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(chunks)}")
        
        # Extract the text to embed
        embedding_text = chunk.get("embedding_text", "")
        
        # Vectorize
        vector = model.encode(embedding_text)
        
        # Add vector to chunk
        chunk_with_vector = {
            **chunk,
            "embedding_vector": vector
        }
        vectorized_chunks.append(chunk_with_vector)
    
    print(f"✓ Vectorization complete ({len(vectorized_chunks)} chunks)")
    return vectorized_chunks

def save_chunks_to_csv(
    vectorized_chunks: List[Dict],
    output_path: str = "knowledge_base.csv",
    book_name: str = "unknown"
) -> str:
    """
    Save vectorized chunks to a CSV file.
    
    Args:
        vectorized_chunks (List[Dict]): List of vectorized chunk dicts.
        output_path (str): Path to save the CSV file.
        book_name (str): Name of the book being processed.
    
    Returns:
        str: Path to the saved CSV file.
    """
    print(f"Converting chunks to DataFrame...")
    
    # Prepare data for DataFrame
    data = []
    for chunk in vectorized_chunks:
        row = {
            "id": chunk["id"],
            "embedding_text": chunk["embedding_text"],
            "book_id": chunk.get("book_id", "unknown"),
            "chapter_name": chunk.get("chapter_name", "Unknown"),
            "subchapter_name": chunk.get("subchapter_name", "Main"),
            "chunk_index": chunk.get("chunk_index", 0),
            "page_number": chunk.get("page_number", 1),
            "token_count": chunk.get("token_count", 0),
            "embedding_vector": chunk.get("embedding_vector").tolist() if isinstance(chunk.get("embedding_vector"), np.ndarray) else chunk.get("embedding_vector")
        }
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save to CSV
    print(f"Saving to CSV: {output_path}")
    df.to_csv(output_path, index=False)
    print(f"✓ CSV saved successfully ({len(df)} rows)")
    
    return output_path

def load_chunks_from_csv(csv_path: str) -> tuple[pd.DataFrame, List[np.ndarray]]:
    """
    Load chunks and vectors from CSV file.
    
    Args:
        csv_path (str): Path to the CSV file.
    
    Returns:
        Tuple of (DataFrame, List of vectors as numpy arrays)
    """
    print(f"Loading chunks from CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Convert embedding vectors back to numpy arrays
    vectors = []
    for vector_str in df["embedding_vector"]:
        if isinstance(vector_str, str):
            import json
            vector = np.array(json.loads(vector_str))
        else:
            vector = np.array(vector_str)
        vectors.append(vector)
    
    print(f"✓ Loaded {len(df)} chunks from CSV")
    return df, vectors