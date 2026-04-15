# 📚 Book Retrieval-Augmented Generation (RAG) System v2

A system for extracting knowledge from PDF books using intelligent token-based chunking, storing in CSV, and answering user queries with AI-powered summarization.

## ✨ Latest Updates (V2)

- **Token-Based Chunking**: Fixed-size token chunks (300 tokens default) with configurable overlap (50 tokens)
- **CSV Storage**: Lightweight, human-readable knowledge base format
- **LLM Integration**: Support for multiple free LLM providers (Ollama, HuggingFace, OpenAI)
- **Enhanced Metadata**: Proper chunk IDs with book name, chapter, and sequence tracking
- **AI-Powered Answers**: Automatic summarization of retrieved context using LLMs

## 🎯 Features

✅ **Smart PDF Processing**: Extract text while preserving document structure
✅ **Token-Accurate Chunking**: Uses tiktoken for precise token counting (same as OpenAI)
✅ **CSV Knowledge Base**: Easy to inspect, modify, and extend
✅ **Vector Embeddings**: High-quality embeddings via SentenceTransformers
✅ **Fast Similarity Search**: Cosine similarity matching
✅ **Multiple LLM Options**: Ollama (free, local), HuggingFace API (free tier), OpenAI
✅ **Rich Metadata**: Track book, chapter, page numbers, and token counts
✅ **Interactive UI**: Streamlit-based web interface

## 🗂️ Project Structure

```
knowledgable-system/
├── data-preprocess/
│   ├── pdf_processor.py              # PDF text extraction
│   ├── token_chunking.py             # Token-based chunking with overlap
│   ├── chunk_vect.py                 # Vectorization & CSV export
│   ├── knowledge_base.py             # CSV-based search & retrieval
│   ├── llm_integration.py            # LLM providers (Ollama, HF, OpenAI)
│   ├── app.py                        # Streamlit web interface
│   └── 4llm-output.md                # Sample output
├── book.pdf                          # Your PDF book here
├── knowledge_base/                   # Generated knowledge base (auto-created)
│   └── knowledge_base.csv            # Main CSV with chunks & vectors
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── run.bat                           # Windows launcher
└── run.py                            # Cross-platform launcher
```

## 📦 Installation

### 1. Clone or Download Project

```bash
cd app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Alternatively, the launcher scripts will install them automatically.

### 3. Download & Setup LLM (Optional but Recommended)

**Option A: Ollama (Recommended - Free, Local, No API Key)**
```bash
# Download from https://ollama.ai
# After installation, run:
ollama pull mistral
# Or try: ollama pull llama2, ollama pull neural-chat
```

**Option B: HuggingFace (Free tier with limited requests)**
- Get free API key: https://huggingface.co/inference-api

**Option C: OpenAI (Paid, but free credits for new accounts)**
- Get API key: https://platform.openai.com/account/api-keys

## 🚀 Quick Start

### Manual Launch
```bash
cd app
streamlit run app.py
```

The app opens at `http://localhost:<port>`

## 📖 How to Use

### Step 1: Configure Settings (Sidebar)

1. **Embedding Model**: Choose SentenceTransformer model
   - `all-MiniLM-L6-v2` (fast, good quality) ⭐
   - `all-mpnet-base-v2` (best quality, slower)
   - `paraphrase-MiniLM-L6-v2` (good for paraphrasing)

2. **Chunking Parameters**
   - Set token size (recommended: 300)
   - Set overlap (recommended: 50)
   - Overlap helps maintain context between chunks

3. **LLM Provider**
   - Ollama (free, local) - recommended
   - HuggingFace API (free tier)
   - OpenAI (paid)

### Step 2: Upload & Process PDF (Tab 1)

1. Click "Upload a PDF file"
2. Select your book
3. Click "Process PDF"
4. Wait for processing (time depends on PDF size)
5. View statistics and sample chunks

**Processing Steps:**
```
PDF Upload
    ↓
Extract Text (preserves structure)
    ↓
Token-Based Chunking (300 tokens, 50 overlap)
    ↓
Vectorize with SentenceTransformers
    ↓
Save to knowledge_base.csv
    ↓
Ready for queries!
```

### Step 3: Query & Get Answers (Tab 2)

1. Enter your question: "What is TCP/IP?"
2. Adjust Top-K results if desired
3. Click "Search & Answer"
4. View retrieved chunks sorted by relevance
5. See AI-generated answer using LLM

## 📊 CSV Knowledge Base Format

Each row represents one chunk:

| Field | Description |
|-------|-------------|
| `id` | Unique ID: book_name_chapter_name_chunk_number |
| `embedding_text` | The actual text (up to 300 tokens) |
| `embedding_vector` | JSON array of vector values (384/768-dim depending on model) |
| `book_id` | Book identifier |
| `chapter_name` | Chapter name |
| `subchapter_name` | Sub-chapter/section name |
| `chunk_index` | Order within chapter |
| `page_number` | PDF page number |
| `token_count` | Actual tokens in this chunk |

Example:
```
id: computer_networks_main_content_0
book_id: computer_networks
chapter_name: Main
subchapter_name: Content
chunk_index: 0
page_number: 1
token_count: 298
```

## 🤖 LLM Providers

### 1. Ollama (Recommended)
**Free, runs locally on your machine**
- No API keys needed
- Complete privacy
- Works offline

**Setup:**
```bash
# Download from https://ollama.ai
# Run server:
ollama serve
# In another terminal:
ollama pull mistral
```

**Models:**
- `mistral` - Fast, good quality
- `llama2` - Slower, better quality
- `neural-chat` - Good for Q&A
- `dolphin-mixtral` - Mixture of experts

### 2. OpenRouter (100+ Models)
**Access to 100+ LLMs through unified interface**
- Free tier available
- Easy model switching
- Lower cost than direct APIs
- Includes free models (Mistral, Llama 2)

**Setup:**
- Get free API key: https://openrouter.io/keys
- Paste in sidebar

**Popular Models:**
- `Mistral 7B` (Free) - Fast and efficient
- `Llama 2 70B` (Free) - High quality
- `Claude 3 Opus` (Premium) - Best reasoning
- `GPT-4` (Premium) - Most powerful
- `Grok-1` (Premium) - Advanced reasoning

**Why Use OpenRouter:**
- Best for trying multiple models without switching providers
- Free tier includes quality models
- Easily compare model quality/cost
- Recommended if you like to experiment ⭐

### 3. OpenAI API
**Paid (free credits for new accounts)**
- Best quality responses
- Most reliable
- Official GPT-4 and GPT-3.5 access

### 4. HuggingFace Inference API
**Free tier with rate limits**
- Easy to use
- No setup needed
- Limited free requests per day

### 3. OpenAI API
**Paid (free credits for new accounts)**
- Best quality responses
- More reliable
- Steeper learning curve

## 🔧 Configuration Examples

### For Academic Research (High Accuracy)
```
Embedding Model: all-mpnet-base-v2 (best quality)
Chunk Size: 400 tokens (more context)
Overlap: 75 tokens
LLM: OpenAI GPT-4 or Ollama mistral
Top-K: 10 (more sources)
```

### For Fast Prototyping
```
Embedding Model: all-MiniLM-L6-v2 (fast)
Chunk Size: 256 tokens (smaller)
Overlap: 32 tokens
LLM: Ollama mistral (instant, free)
Top-K: 3 (fewer results)
```

## 💡 Example Queries

```
"What is the OSI model?"
"Explain how TCP works"
"What are the security implications of..."
"Summarize the key concepts in Chapter 3"
"How does congestion control work?"
"What is the difference between X and Y?"
```


## 🔮 Future Enhancements (V3+)

- [ ] Cross-Encoder Reranking (better relevance)
- [ ] Multi-PDF Support (knowledge across books)
- [ ] Chat Memory (conversation context)
- [ ] Chapter Auto-Detection
- [ ] Table/Figure Extraction
- [ ] PDF Annotation Support
- [ ] Advanced Filtering (by chapter/date)
- [ ] Export Results (PDF/Word)
- [ ] Performance Analytics
- [ ] Database Backend (SQLite/PostgreSQL)

## 📝 Example Workflow

```python
# 1. User uploads "computer-networks.pdf"
# 2. System extracts: 45,000 tokens of text
# 3. Creates chunks: 150 chunks (300 tokens each)
# 4. Vectorizes: 150 vectors (384-dimensional)
# 5. Saves CSV: knowledge_base/knowledge_base.csv
#
# 6. User asks: "What is TCP?"
# 7. Query vectorized
# 8. Similarity search: top-5 chunks retrieved
# 9. LLM summarizes: "TCP is..."
# 10. User gets answer!
```