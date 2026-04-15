# 🚀 Quick Start Guide - Book RAG System v2

## 5-Minute Setup

### Step 1: Install Dependencies (2 min)
```bash
cd app
pip install -r requirements.txt
```

### Step 2: Download LLM - Choose ONE (2-3 min)

#### Option A: Ollama (Recommended - Free, No API Key) <h3>(Disclaimer: Doesn't work yet)</h3>
```bash
# 1. Download from https://ollama.ai
# 2. After installation, in a terminal run:
ollama serve
# 3. Keep this running. In another terminal:
ollama pull mistral
```

#### Option B: OpenRouter (FREE with 100+ Models)
<h3> Working Option </h3>

```
# 1. Sign up (free tier available): https://openrouter.io/keys
# 2. Get your API key
# 3. You'll paste it into the sidebar in app
# Free models available: Mistral, Llama 2, and more!
```

#### Option C: HuggingFace (Free Tier) <h3>(Disclaimer: Doesn't work yet)</h3>
- Go to https://huggingface.co/inference-api
- Get your API key
- You'll paste it into the sidebar in app

#### Option D: OpenAI (Paid)
- Go to https://platform.openai.com/account/api-keys
- Get your API key
- You'll paste it into the sidebar in app

### Step 3: Run the App (1 min)

**Manual:**
```bash
cd app
streamlit run app.py
```

App opens at: http://localhost:<port>

---

## 🎯 First Time Use

### Tab 1: Upload & Process PDF
1. Click "Upload a PDF file"
2. Select a PDF (test with a small one first)
3. Click "Process PDF" button
4. Watch the progress...
5. Check the sample chunks at the bottom
6. ✅ done!

### Tab 2: Query Knowledge Base
1. Type a question: "What does X mean?"
2. Click "Search & Answer"
3. 🎉 See results + AI answer!

---

## ⚙️ Sidebar Settings

**Embedding Model:**
- Use default `all-MiniLM-L6-v2` if unsure

**Chunk Size & Overlap:**
- Default values (300, 50) are good to start

**LLM Provider:**
- **Ollama**: Download from https://ollama.ai, run `ollama serve`
- **OpenRouter**: Get free API key from https://openrouter.io/keys (FEW MODELS FREE!)
- **OpenAI**: Paid, get key from https://platform.openai.com
- **HuggingFace**: Free tier, get key from https://huggingface.co/inference-api

**Knowledge Base:**
- Shows status
- Can clear if needed

---

## 📝 Example Workflow

```bash
# 1. Terminal 1: Start your LLM provider
# Option A: Ollama
ollama serve

# Option B: OpenRouter (just get API key, no setup needed)
# Just add it in the app!

# 2. Terminal 2: Start Streamlit app
cd app/data-preprocess
streamlit run app.py

# 3. Browser: http://localhost:8501
# → Upload "Computer_Networks.pdf"
# → Click "Process PDF"
# → Wait 5-10 minutes
# → Go to "Query Knowledge Base" tab
# → Ask: "What is TCP?"
# → Get instant AI-powered answer!
```

---

## ✨ What's New in v2

| Feature | What Changed |
|---------|-------------|
| Storage | FAISS → CSV (human-readable!) |
| Chunking | Paragraph → Token-based (300 tokens) |
| Answers | Retrieval only → AI-powered answers |
| Config | Fixed → Adjustable sliders |

---

## 🆘 Common Issues

### "ModuleNotFoundError: No module named 'tiktoken'"
```bash
pip install tiktoken pandas requests
```

### "Ollama not connecting"
```bash
# Make sure Ollama is running in another terminal
ollama serve
```

### "API rate limit exceeded"
- HuggingFace free tier has limits
- Try Ollama (unlimited, local)

### "Process takes forever"
- First time: model downloads (~500MB)
- Large PDFs: takes time proportional to size
- Be patient! ☕

---

## 💡 Tips & Tricks

✅ **Start small** - Test with 10-20 page PDFs first
✅ **Use Ollama** - Simplest, no API keys needed
✅ **Adjust chunks** - Smaller = faster, larger = more context
✅ **Inspect CSV** - You can open it in Excel!
✅ **Multiple PDFs** - Process different books to different CSVs

---

## 📚 What You Can Ask

```
"Define X"
"Explain how Y works"
"What's the difference between A and B?"
"Summarize Chapter 3"
"What are the main concepts?"
"How does X impact Y?"
"When was X introduced?"
```

---

## 🎓 Full Documentation

- **README.md** - Complete guide with all features
---

## 🚀 You're Ready!

That's it! You now have a fully functional Book RAG system with:
- ✅ PDF upload & processing
- ✅ Smart token-based chunking
- ✅ Vector similarity search
- ✅ AI-powered question answering