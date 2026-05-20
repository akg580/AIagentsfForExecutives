# RAG Executive Analyst
**AI-Powered Business Intelligence & Reporting Platform**

> Enterprise-grade RAG system that ingests internal documents, retrieves semantically relevant evidence, and generates structured, cited executive reports in under 60 seconds.

## Stack (100% Free Tier)
| Layer | Technology | Why |
|---|---|---|
| LLM | Groq API (`llama-3.3-70b-versatile`) | Free tier, 6000 tokens/min |
| Embeddings | `all-MiniLM-L6-v2` (local) | No API cost, runs on CPU |
| Vector DB | ChromaDB (local) | Zero infra, persistent on disk |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Free OSS, +15% MRR |
| Web Search | Tavily API (free tier) | 1000 searches/month free |
| Backend | FastAPI + Uvicorn | Production-grade async |
| Frontend | Streamlit | Rapid UI, zero frontend code |
| Export | python-docx | Free, DOCX with citations |

## Quickstart

```bash
# 1. Clone & enter
git clone <repo> && cd rag-executive-analyst

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env with your API keys (Groq + Tavily — both free)

# 5. Run backend
uvicorn backend.main:app --reload --port 8000

# 6. Run frontend (new terminal)
streamlit run frontend/app.py
```

## Get Free API Keys
- **Groq**: https://console.groq.com → Create API Key (free, no credit card)
- **Tavily**: https://tavily.com → Sign up → API Keys (1000 free searches/month)

## File Structure
```
rag-executive-analyst/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment & settings
│   ├── api/routes/
│   │   ├── documents.py         # Upload, list, delete docs
│   │   ├── query.py             # NL query → cited answer
│   │   └── reports.py          # Generate, export reports
│   ├── core/
│   │   ├── ingestion/
│   │   │   ├── loader.py        # PDF/DOCX/XLSX file loading
│   │   │   ├── chunker.py       # Recursive text splitting
│   │   │   └── embedder.py      # Local sentence-transformer
│   │   ├── retrieval/
│   │   │   ├── vectorstore.py   # ChromaDB wrapper
│   │   │   ├── retriever.py     # ANN search + rerank
│   │   │   └── reranker.py      # Cross-encoder reranking
│   │   ├── generation/
│   │   │   ├── llm.py           # Groq LLM client
│   │   │   ├── agent.py         # ReAct agent loop
│   │   │   └── templates.py     # Report section templates
│   │   ├── tools/
│   │   │   ├── web_search.py    # Tavily web search tool
│   │   │   └── doc_retriever.py # Internal retrieval tool
│   │   └── export/
│   │       └── docx_exporter.py # Cited DOCX export
│   ├── models/                  # Pydantic schemas
│   └── utils/                   # Logger, validators
├── frontend/
│   ├── app.py                   # Streamlit entry
│   └── pages/                   # Multi-page UI
└── tests/                       # Unit tests
```

## API Docs
After running the backend, visit: http://localhost:8000/docs
