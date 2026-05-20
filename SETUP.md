# SETUP GUIDE — RAG Executive Analyst
## Step-by-step for VS Code

---

## 1. Prerequisites (one-time install)

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | https://python.org |
| VS Code | Latest | https://code.visualstudio.com |
| Git | Any | https://git-scm.com |

---

## 2. Open in VS Code

```bash
# Open the workspace file directly — VS Code will configure automatically
code rag-executive-analyst.code-workspace
```

Or: **File → Open Workspace from File → select `rag-executive-analyst.code-workspace`**

---

## 3. Create virtual environment

```bash
# In VS Code terminal (Ctrl + `)
python -m venv venv

# Activate
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows PowerShell
```

Select the interpreter in VS Code: `Ctrl+Shift+P → Python: Select Interpreter → ./venv/bin/python`

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

This will download:
- Groq Python SDK
- ChromaDB (local vector DB)
- sentence-transformers + model (~90MB, auto-downloaded on first run)
- FastAPI + Uvicorn
- Streamlit

**First run takes 2–5 min** (downloads embedding model & reranker).

---

## 5. Get free API keys (2 minutes)

### Groq (LLM — free, no credit card)
1. Go to https://console.groq.com
2. Sign up → Dashboard → API Keys → Create API Key
3. Copy the key starting with `gsk_`

### Tavily (Web Search — free, 1000 searches/month)
1. Go to https://tavily.com
2. Sign up → Dashboard → Copy your API key starting with `tvly-`

---

## 6. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in:
```
GROQ_API_KEY=gsk_your_key_here
TAVILY_API_KEY=tvly-your_key_here
```

Everything else can stay as defaults.

---

## 7. Run the application

### Option A — VS Code Launch Configs (recommended)
Press `F5` → Select **"FastAPI Backend"** → Run

Then open a new terminal and press `F5` → **"Streamlit Frontend"**

### Option B — Terminal
```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
streamlit run frontend/app.py
```

### Option C — Single script
```bash
bash scripts/start.sh
```

---

## 8. Access the app

| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health check | http://localhost:8000/api/v1/health |

---

## 9. Using the app

### Step 1: Upload documents
- Open http://localhost:8501
- Click **📁 Upload Documents**
- Upload any PDF, DOCX, or XLSX file (try an annual report, board deck, or research paper)
- Wait for "Successfully ingested" message

### Step 2: Ask questions
- Click **🔍 Ask a Question**
- Type a natural language question
- Choose search mode: **hybrid** (recommended) = internal docs + web
- See cited answer in < 5 seconds

### Step 3: Generate reports
- Click **📄 Generate Report**
- Enter a report title and research question
- Select sections (Executive Summary, Key Findings, etc.)
- Click Generate → Wait 30–60 seconds
- Download as DOCX or Markdown

---

## 10. Run tests

```bash
# From VS Code terminal with venv active
pytest tests/ -v

# Or use VS Code Launch Config:
# F5 → "Run Tests"
```

---

## Project structure recap

```
rag-executive-analyst/
│
├── backend/                          ← FastAPI application
│   ├── main.py                       ← App entry point
│   ├── config.py                     ← All settings (reads .env)
│   ├── api/routes/
│   │   ├── documents.py              ← POST /documents/upload etc.
│   │   ├── query.py                  ← POST /query
│   │   ├── reports.py                ← POST /reports/generate, GET export
│   │   └── health.py                 ← GET /health
│   ├── core/
│   │   ├── ingestion/
│   │   │   ├── loader.py             ← PDF/DOCX/XLSX → pages
│   │   │   ├── chunker.py            ← Pages → overlapping chunks
│   │   │   └── embedder.py           ← Chunks → 384-dim vectors (local)
│   │   ├── retrieval/
│   │   │   ├── vectorstore.py        ← ChromaDB CRUD
│   │   │   ├── retriever.py          ← embed → ANN → rerank pipeline
│   │   │   └── reranker.py           ← Cross-encoder reranking
│   │   ├── generation/
│   │   │   ├── llm.py                ← Groq API client + retry
│   │   │   ├── agent.py              ← ReAct loop: think→act→observe→generate
│   │   │   └── templates.py          ← Section prompts (Executive Summary etc.)
│   │   ├── tools/
│   │   │   ├── doc_retriever.py      ← Internal retrieval tool
│   │   │   └── web_search.py         ← Tavily web search tool
│   │   └── export/
│   │       └── docx_exporter.py      ← Report → cited DOCX
│   ├── models/schemas.py             ← All Pydantic models
│   └── utils/
│       ├── logger.py                 ← Loguru structured logging
│       └── validators.py             ← Input validation helpers
│
├── frontend/                         ← Streamlit UI
│   ├── app.py                        ← Home page + sidebar
│   └── pages/
│       ├── 1_upload.py               ← Document management
│       ├── 2_query.py                ← Q&A interface
│       └── 3_reports.py             ← Report generator + DOCX download
│
├── tests/
│   ├── test_ingestion.py             ← Chunker + embedder unit tests
│   ├── test_retrieval.py             ← Reranker + retriever unit tests
│   └── test_api.py                   ← FastAPI route integration tests
│
├── data/                             ← Auto-created on first run
│   ├── chroma_db/                    ← Persistent vector store
│   ├── uploads/                      ← Saved uploaded files
│   └── reports/                      ← Saved report JSONs
│
├── .env                              ← Your API keys (never commit)
├── .env.example                      ← Template
├── requirements.txt                  ← All dependencies
├── pytest.ini                        ← Test config
└── rag-executive-analyst.code-workspace ← VS Code workspace
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` with venv active |
| `groq.AuthenticationError` | Check `GROQ_API_KEY` in `.env` |
| `chromadb` errors on query | Upload at least one document first |
| Tavily timeout | Check `TAVILY_API_KEY` or use `search_mode=internal` |
| Model download stuck | First run downloads ~200MB — wait 3–5 min |
| Port 8000 in use | `lsof -ti:8000 \| xargs kill -9` |

---

## Free tier limits summary

| Service | Free limit | What happens when exceeded |
|---------|-----------|---------------------------|
| Groq | 6K tokens/min, 500K/day | Rate limit error → auto retry |
| Tavily | 1000 searches/month | Graceful fallback to internal-only |
| ChromaDB | Unlimited (local disk) | Never exceeded |
| Embeddings | Unlimited (runs locally) | Never exceeded |
| Reranker | Unlimited (runs locally) | Never exceeded |
