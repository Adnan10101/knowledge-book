import pathlib
import fitz 

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file, preserving paragraph structure.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        list: A list of paragraphs extracted from the PDF.
    """
    paragraphs = []
    try:
        # Open the PDF file
        with fitz.open(pdf_path) as pdf:
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                text = page.get_text("blocks")  # Extract text blocks
                for block in text:
                    block_text = block[4].strip()
                    if block_text:  # Ignore empty blocks
                        paragraphs.append(block_text)
    except Exception as e:
        print(f"Error processing PDF: {e}")
    return paragraphs

def process_pdf_with_metadata(pdf_path):
    """
    Processes a PDF file and extracts paragraphs with metadata.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        list: A list of dictionaries, each containing a paragraph and its metadata.
    """
    processed_chunks = []
    try:
        with fitz.open(pdf_path) as pdf:
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                text = page.get_text("blocks")
                for block_index, block in enumerate(text):
                    block_text = block[4].strip()
                    if block_text:
                        chunk_metadata = {
                            "paragraph": block_text,
                            "page_number": page_num + 1,
                            "paragraph_index": block_index + 1,
                        }
                        processed_chunks.append(chunk_metadata)
    except Exception as e:
        print(f"Error processing PDF: {e}")
    return processed_chunks