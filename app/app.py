import streamlit as st
import os
import pandas as pd
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Import custom modules
from pdf_processor import process_pdf_with_metadata
from token_chunking import chunk_pdf_content
from chunk_vect import vectorize_chunks, load_chunks_from_csv
from knowledge_base import handle_query
from llm_integration import generate_answer
from chunk_vect import save_chunks_to_csv

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Book RAG System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📚 Book Retrieval-Augmented Generation System")
st.markdown("---")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_kb_csv_path() -> str:
    """Get the knowledge base CSV path."""
    return "knowledge_base/knowledge_base.csv"

def check_kb_exists() -> bool:
    """Check if knowledge base CSV exists."""
    return os.path.exists(get_kb_csv_path())

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model selection
    model_name = st.selectbox(
        "Select Embedding Model",
        [
            "all-MiniLM-L6-v2",
            "all-mpnet-base-v2",
            "paraphrase-MiniLM-L6-v2"
        ],
        help="Choose a SentenceTransformer model for embeddings"
    )
    
    # Top-K selection
    top_k = st.slider(
        "Number of Results to Retrieve (Top-K)",
        min_value=1,
        max_value=20,
        value=5,
        help="Number of most relevant chunks to retrieve"
    )
    
    # Chunking parameters
    st.markdown("---")
    st.header("🔧 Chunking Parameters")
    
    chunk_size = st.slider(
        "Chunk Size (tokens)",
        min_value=100,
        max_value=1000,
        value=300,
        step=50,
        help="Number of tokens per chunk"
    )
    
    overlap_size = st.slider(
        "Overlap Size (tokens)",
        min_value=0,
        max_value=200,
        value=50,
        step=10,
        help="Number of overlapping tokens between chunks"
    )
    
    # LLM Configuration
    st.markdown("---")
    st.header("🤖 LLM Configuration")
    
    llm_provider = st.selectbox(
        "Select LLM Provider",
        ["Ollama (Local - FREE)", "OpenRouter (100+ models)", "OpenAI", "HuggingFace API"],
        help="Choose an LLM for generating answers"
    )
    
    llm_type = None
    llm_kwargs = {}
    
    if llm_provider == "Ollama (Local - FREE)":
        llm_type = "ollama"
        ollama_model = st.selectbox(
            "Ollama Model",
            ["mistral", "llama2", "neural-chat", "dolphin-mixtral"],
            help="Select which model to use with Ollama"
        )
        llm_kwargs = {"model": ollama_model}
        st.info("💡 Download Ollama from https://ollama.ai and run: ollama serve")
    
    elif llm_provider == "OpenRouter (100+ models)":
        llm_type = "openrouter"
        openrouter_api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            help="Get free API key from https://openrouter.io/keys"
        )
        
        # Popular OpenRouter models (including free options)
        openrouter_models = {
            "Mistral 7B (Free)": "mistralai/mistral-7b-instruct:free",
            "Google gemini-2.0-flash":"google/gemini-2.0-flash-001",
            "Llama 2 70B (Free)": "meta-llama/llama-2-70b-chat:free",
            "Neural Chat 7B": "intel/neural-chat-7b",
            "OpenChat 3.5": "openchat/openchat-3.5",
            "Grok-1": "gryphe/grok-1",
            "Claude 3 Opus": "anthropic/claude-3-opus",
            "Claude 3 Sonnet": "anthropic/claude-3-sonnet",
            "GPT-4": "openai/gpt-4",
            "GPT-3.5": "openai/gpt-3.5-turbo",
        }
        
        selected_model_name = st.selectbox(
            "OpenRouter Model",
            list(openrouter_models.keys()),
            help="Choose from 100+ available models. Free tier available!"
        )
        
        llm_kwargs = {
            "api_key": openrouter_api_key,
            "model": openrouter_models[selected_model_name]
        }
        st.info(f"💡 Using: {selected_model_name} | Free tier available at https://openrouter.io")
    
    elif llm_provider == "OpenAI":
        llm_type = "openai"
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Get API key from https://platform.openai.com/account/api-keys"
        )
        openai_model = st.selectbox(
            "OpenAI Model",
            ["gpt-3.5-turbo", "gpt-4"],
            help="Select model"
        )
        llm_kwargs = {"api_key": openai_api_key, "model": openai_model}
        st.info("💰 Requires paid API key")
    
    else:  # HuggingFace API
        llm_type = "huggingface"
        hf_api_key = st.text_input(
            "HuggingFace API Key",
            type="password",
            help="Get free API key from https://huggingface.co/inference-api"
        )
        llm_kwargs = {"api_key": hf_api_key}
        st.info("💡 Free tier available with limited requests")
    
    # Knowledge Base Management
    st.markdown("---")
    st.header("📖 Knowledge Base")
    
    kb_exists = check_kb_exists()
    
    if kb_exists:
        st.success("✅ Knowledge Base Loaded")
        kb_path = get_kb_csv_path()
        try:
            df, _ = load_chunks_from_csv(kb_path)
            st.metric("Total Chunks", len(df))
            st.metric("Book", df.iloc[0]["book_id"] if len(df) > 0 else "N/A")
        except:
            pass
        
        if st.button("🗑️ Clear Knowledge Base", key="clear_kb"):
            import shutil
            shutil.rmtree("knowledge_base", ignore_errors=True)
            st.session_state.df = None
            st.session_state.vectors = None
            st.success("✅ Cleared!")
            st.rerun()
    else:
        st.info("ℹ️ No KB loaded yet")

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if "df" not in st.session_state:
    st.session_state.df = None
if "vectors" not in st.session_state:
    st.session_state.vectors = None
if "model" not in st.session_state:
    st.session_state.model = None

# Load existing knowledge base
if st.session_state.df is None and check_kb_exists():
    kb_path = get_kb_csv_path()
    try:
        st.session_state.df, st.session_state.vectors = load_chunks_from_csv(kb_path)
        st.session_state.model = SentenceTransformer(model_name)
    except:
        pass

# ============================================================================
# TAB 1: UPLOAD AND PROCESS PDF
# ============================================================================

tab1, tab2 = st.tabs(["📤 Upload & Process PDF", "🔍 Query Knowledge Base"])

with tab1:
    st.header("Upload and Process a Book PDF")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload a PDF file",
            type=["pdf"],
            help="Select a PDF book to process"
        )
    
    with col2:
        process_button = st.button("🔄 Process PDF", use_container_width=True)
    
    if uploaded_file is not None:
        st.info(f"📄 Selected file: {uploaded_file.name}")
        
        if process_button:
            with st.spinner("Processing PDF..."):
                # Save uploaded file temporarily
                temp_pdf_path = f"temp_{uploaded_file.name}"
                with open(temp_pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    # Step 1: Extract text from PDF
                    st.write("Step 1: Extracting text from PDF...")
                    pdf_chunks_metadata = process_pdf_with_metadata(temp_pdf_path)
                    full_text = " ".join([chunk["paragraph"] for chunk in pdf_chunks_metadata])
                    st.success(f"✅ Extracted text")
                    
                    # Step 2: Create token-based chunks
                    st.write(f"Step 2: Creating chunks ({chunk_size} tokens, {overlap_size} overlap)...")
                    book_name = uploaded_file.name.replace(".pdf", "")
                    chunks = chunk_pdf_content(
                        full_text,
                        book_name=book_name,
                        chunk_size=chunk_size,
                        overlap_size=overlap_size
                    )
                    st.success(f"✅ Created {len(chunks)} chunks")
                    
                    # Step 3: Vectorize chunks
                    st.write(f"Step 3: Vectorizing chunks using {model_name}...")
                    model = SentenceTransformer(model_name)
                    vectorized_chunks = vectorize_chunks(chunks, model_name)
                    st.success(f"✅ Vectorized {len(vectorized_chunks)} chunks")
                    
                    # Step 4: Save to CSV
                    st.write("Step 4: Saving to CSV...")
                    
                    kb_path = get_kb_csv_path()
                    os.makedirs("knowledge_base", exist_ok=True)
                    save_chunks_to_csv(vectorized_chunks, kb_path, book_name)
                    
                    # Step 5: Load into session state
                    st.write("Step 5: Loading into memory...")
                    df, vectors = load_chunks_from_csv(kb_path)
                    st.session_state.df = df
                    st.session_state.vectors = vectors
                    st.session_state.model = model
                    
                    st.success("✅ Knowledge Base Created!")
                    
                    # Display statistics
                    st.markdown("---")
                    st.subheader("📊 Processing Statistics")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Chunks", len(chunks))
                    with col2:
                        st.metric("Embedding Model", model_name.split("-")[-1])
                    with col3:
                        st.metric("Vector Dimension", len(vectorized_chunks[0]["embedding_vector"]))
                    with col4:
                        st.metric("Chunk Size", f"{chunk_size} tokens")
                    
                    # Display sample chunks
                    st.markdown("---")
                    st.subheader("📝 Sample Chunks (First 5)")
                    for i in range(min(5, len(df))):
                        chunk = df.iloc[i]
                        with st.expander(f"Chunk {i+1} - {chunk['id']}"):
                            st.write(f"**ID:** {chunk['id']}")
                            st.write(f"**Page:** {chunk['page_number']}")
                            st.write(f"**Tokens:** {chunk['token_count']}")
                            st.write(f"**Content:**\n\n{chunk['embedding_text']}")
                
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {e}")
                    import traceback
                    st.error(traceback.format_exc())
                
                finally:
                    if os.path.exists(temp_pdf_path):
                        os.remove(temp_pdf_path)

# ============================================================================
# TAB 2: QUERY KNOWLEDGE BASE
# ============================================================================

with tab2:
    st.header("Query Your Knowledge Base")
    
    # Check if knowledge base is loaded
    if st.session_state.df is None:
        st.warning("⚠️ No knowledge base loaded. Please upload and process a PDF first.")
    else:
        st.success(f"✅ Knowledge Base Ready ({len(st.session_state.df)} chunks)")
        
        # Query input
        st.markdown("---")
        query_text = st.text_area(
            "Enter your question:",
            placeholder="e.g., What is TCP/IP?",
            help="Ask a question about the book"
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_button = st.button("🔍 Search & Answer", use_container_width=True)
        
        with col2:
            st.metric("Top-K Results", top_k)
        
        if search_button and query_text:
            with st.spinner("Searching knowledge base..."):
                try:
                    # Query the knowledge base
                    results = handle_query(
                        query_text,
                        st.session_state.model,
                        st.session_state.df,
                        st.session_state.vectors,
                        top_k=top_k
                    )
                    
                    st.markdown("---")
                    st.subheader(f"🎯 Retrieved {len(results)} Context Chunks")
                    
                    # Display retrieved chunks
                    retrieved_chunks = []
                    for idx, result in enumerate(results):
                        similarity = result["similarity"]
                        metadata = result["metadata"]
                        
                        # Create badge
                        if similarity > 0.8:
                            badge_color = "🟢"
                        elif similarity > 0.6:
                            badge_color = "🟡"
                        else:
                            badge_color = "🔵"
                        
                        retrieved_chunks.append(result)
                        
                        with st.expander(
                            f"{badge_color} Chunk {idx+1} (Page {metadata.get('page_number', 'N/A')}) | Similarity: {similarity:.2%}",
                            expanded=(idx == 0)
                        ):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write(metadata.get("embedding_text", ""))
                            
                            with col2:
                                st.metric("Similarity", f"{similarity:.2%}")
                    
                    # Generate LLM response
                    st.markdown("---")
                    st.subheader("🤖 AI Response")
                    
                    with st.spinner("Generating answer using LLM..."):
                        try:
                            answer = generate_answer(
                                query_text,
                                retrieved_chunks,
                                provider_type=llm_type,
                                max_tokens=500,
                                **llm_kwargs
                            )
                            st.markdown(answer)
                        
                        except Exception as e:
                            st.error(f"❌ Error generating LLM response: {str(e)}")
                            st.info("💡 LLM Setup Instructions:")
                            st.info("- **Ollama**: Download from https://ollama.ai, run `ollama serve`, then `ollama pull mistral`")
                            st.info("- **HuggingFace**: Get free API key from https://huggingface.co/inference-api")
                            st.info("- **OpenAI**: Get API key from https://platform.openai.com/account/api-keys")
                    
                    # Summary statistics
                    st.markdown("---")
                    st.subheader("📈 Search Statistics")
                    avg_similarity = sum(r['similarity'] for r in results) / len(results) if results else 0
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Average Similarity", f"{avg_similarity:.2%}")
                    with col2:
                        st.metric("Best Match", f"{max(r['similarity'] for r in results):.2%}")
                
                except Exception as e:
                    st.error(f"❌ Error during search: {e}")
                    import traceback
                    st.error(traceback.format_exc())
        
        elif search_button and not query_text:
            st.warning("⚠️ Please enter a query first")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    📚 Book RAG System | Token-Based Chunking | CSV Storage | LLM Powered Answers
    </div>
    """,
    unsafe_allow_html=True
)

