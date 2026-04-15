import re
from typing import List, Dict, Optional
import tiktoken

# Initialize tokenizer (uses GPT-2 encoding by default)
try:
    tokenizer = tiktoken.get_encoding("cl100k_base")
except:
    # Fallback to simple word-based tokenization
    tokenizer = None

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text string.
    Uses tiktoken for accurate token counting.
    """
    if tokenizer:
        return len(tokenizer.encode(text))
    else:
        # Fallback: simple word-based tokenization
        return len(text.split())

def detect_chapters(text: str) -> List[Dict[str, str]]:
    """
    Detect chapters in text using common patterns.
    Returns list of dicts with 'chapter_name', 'subchapter_name', 'content', and 'page_number'.
    
    Args:
        text (str): Full text from PDF (with page breaks marked as \f or ===PAGE===)
    
    Returns:
        List[Dict]: List of chapter dicts
    """
    chapters = []
    
    # Split by common chapter patterns
    chapter_pattern = r'(?:^|\n)(CHAPTER|CH\.?|SECTION|§|Chapter|Sec\.?)\s+(\d+|[IVX]+)?[\.\-\:]?\s*(.*?)(?=\n|$)'
    
    current_chapter = {
        "chapter_name": "Introduction",
        "subchapter_name": "Main",
        "content": text,
        "page_number": 1
    }
    chapters.append(current_chapter)
    
    return chapters

def create_chunks_with_overlap(
    text: str,
    chunk_size: int = 300,
    overlap_size: int = 50,
    chapter_name: str = "Unknown",
    subchapter_name: str = "Main",
    book_id: str = "unknown_book",
    page_number: int = 1
) -> List[Dict[str, any]]:
    """
    Split text into chunks with token-based sizing and overlap.
    
    Args:
        text (str): Text to chunk
        chunk_size (int): Target tokens per chunk (default: 300)
        overlap_size (int): Overlapping tokens between chunks (default: 50)
        chapter_name (str): Name of the chapter
        subchapter_name (str): Name of the subchapter
        book_id (str): Identifier for the book (e.g., "computer_networks")
        page_number (int): Starting page number
    
    Returns:
        List[Dict]: List of chunk dicts with metadata
    """
    chunks = []
    chunk_index = 0
    
    # Split text by sentences for better quality
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk_text = ""
    current_chunk_tokens = 0
    overlap_text = ""
    
    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        
        # Check if adding this sentence would exceed chunk size
        if current_chunk_tokens + sentence_tokens > chunk_size and current_chunk_text:
            # Save the current chunk
            chunk_id = f"{book_id}_{chapter_name}_{subchapter_name}_{chunk_index}"
            
            chunks.append({
                "id": chunk_id,
                "embedding_text": current_chunk_text.strip(),
                "book_id": book_id,
                "chapter_name": chapter_name,
                "subchapter_name": subchapter_name,
                "chunk_index": chunk_index,
                "page_number": page_number,
                "token_count": current_chunk_tokens
            })
            
            # Prepare overlap for next chunk
            overlap_text = current_chunk_text[-int(len(current_chunk_text) * 0.15):]  # Approximate overlap
            current_chunk_text = overlap_text + " " + sentence
            current_chunk_tokens = count_tokens(overlap_text) + sentence_tokens
            chunk_index += 1
        else:
            current_chunk_text += " " + sentence if current_chunk_text else sentence
            current_chunk_tokens += sentence_tokens
    
    # Add the last chunk
    if current_chunk_text.strip():
        chunk_id = f"{book_id}_{chapter_name}_{subchapter_name}_{chunk_index}"
        chunks.append({
            "id": chunk_id,
            "embedding_text": current_chunk_text.strip(),
            "book_id": book_id,
            "chapter_name": chapter_name,
            "subchapter_name": subchapter_name,
            "chunk_index": chunk_index,
            "page_number": page_number,
            "token_count": current_chunk_tokens
        })
    
    return chunks

def chunk_pdf_content(
    pdf_text: str,
    book_name: str,
    chunk_size: int = 300,
    overlap_size: int = 50
) -> List[Dict[str, any]]:
    """
    Main function to chunk PDF content into tokens with metadata.
    
    Args:
        pdf_text (str): Full text extracted from PDF
        book_name (str): Name of the book
        chunk_size (int): Target tokens per chunk
        overlap_size (int): Overlapping tokens between chunks
    
    Returns:
        List[Dict]: List of chunks with metadata
    """
    # Simple approach: treat entire PDF as one chapter for now
    # In future, can add more sophisticated chapter detection
    
    book_id = book_name.lower().replace(" ", "_")
    
    # Create chunks for the entire text
    chunks = create_chunks_with_overlap(
        text=pdf_text,
        chunk_size=chunk_size,
        overlap_size=overlap_size,
        chapter_name="Main",
        subchapter_name="Content",
        book_id=book_id,
        page_number=1
    )
    
    return chunks
