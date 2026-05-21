"""
frontend/app.py
────────────────
Enterprise home dashboard — RAG Executive Analyst.
Design: Obsidian dark · Space Grotesk · Indigo/Amber palette.
"""
import streamlit as st
import requests
from frontend.components.styles import get_css, sidebar_html, page_header, kpi_grid, section_label

st.set_page_config(
    page_title="RAG Executive Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject design system ──────────────────────────────────────────────────────
st.markdown(get_css(), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(sidebar_html(), unsafe_allow_html=True)
    st.markdown('<div class="rea-sidebar-section">Navigation</div>', unsafe_allow_html=True)

    pages = [
        ("🏠", "Home", "app",        True),
        ("📁", "Upload Documents", "pages/1_upload", False),
        ("🔍", "Ask a Question",  "pages/2_query",  False),
        ("📄", "Generate Report", "pages/3_reports",False),
    ]
    for icon, label, _, active in pages:
        cls = "active" if active else ""
        st.markdown(
            f'<div class="rea-nav-item {cls}">{icon}&nbsp;&nbsp;{label}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="rea-sidebar-section">System</div>', unsafe_allow_html=True)

    # Live health check
    try:
        h = requests.get("http://localhost:8000/api/v1/health", timeout=2).json()
        status_dot = '<span class="rea-dot green"></span>'
        status_txt = "Online"
        chroma_stat = h.get("services", {}).get("chromadb", "—")
        chunks = chroma_stat.split("|")[1].strip().split(" ")[0] if "|" in chroma_stat else "—"
    except Exception:
        status_dot = '<span class="rea-dot red"></span>'
        status_txt = "Offline"
        chunks = "—"

    st.markdown(f"""
<div class="rea-sidebar-stat">
  <span>API Status</span>
  <span class="rea-sidebar-stat-val">{status_dot}{status_txt}</span>
</div>
<div class="rea-sidebar-stat">
  <span>Chunks indexed</span>
  <span class="rea-sidebar-stat-val">{chunks}</span>
</div>
<div class="rea-sidebar-stat">
  <span>LLM</span>
  <span class="rea-sidebar-stat-val">Groq·llama-3.3</span>
</div>
<div class="rea-sidebar-stat">
  <span>Vector DB</span>
  <span class="rea-sidebar-stat-val">ChromaDB</span>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="rea-sidebar-section">Links</div>', unsafe_allow_html=True)
    st.markdown("""
<div style="padding: 0 0.75rem; display:flex; flex-direction:column; gap:4px">
  <a href="http://localhost:8000/docs" target="_blank" class="rea-nav-item">📚 API Docs (Swagger)</a>
  <a href="http://localhost:8000/api/v1/health" target="_blank" class="rea-nav-item">❤️ Health Check</a>
  <a href="https://github.com/akg580/AIagentsfForExecutives" target="_blank" class="rea-nav-item">🐙 GitHub Repo</a>
</div>
""", unsafe_allow_html=True)

# ── Hero header ───────────────────────────────────────────────────────────────
st.markdown(page_header(
    title="RAG Executive Analyst",
    subtitle="AI-powered business intelligence — query internal documents, retrieve cited evidence, generate boardroom-ready reports in under 60 seconds.",
    badge="● Enterprise AI Platform",
    badge_type="indigo",
), unsafe_allow_html=True)

# ── KPI strip ─────────────────────────────────────────────────────────────────
st.markdown(kpi_grid([
    {"label": "Report Generation", "value": "< 60s",    "sub": "end-to-end latency",      "color": "indigo"},
    {"label": "Retrieval Accuracy", "value": "85%+",    "sub": "MRR after reranking",      "color": "amber"},
    {"label": "Citation Rate",      "value": "100%",    "sub": "hard validation gate",     "color": "emerald"},
    {"label": "Infra Cost",         "value": "$0/mo",   "sub": "free tier stack",          "color": "sky"},
]), unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown(section_label("HOW IT WORKS"), unsafe_allow_html=True)

st.markdown("""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:2rem">
  <div class="rea-step-card">
    <span class="rea-step-num">Step 01</span>
    <span class="rea-step-emoji">📁</span>
    <div class="rea-step-title">Upload Documents</div>
    <div class="rea-step-desc">Index PDFs, DOCX, or XLSX files. Chunked into 500-token overlapping segments, embedded with all-MiniLM-L6-v2, stored in ChromaDB.</div>
  </div>
  <div class="rea-step-card">
    <span class="rea-step-num">Step 02</span>
    <span class="rea-step-emoji">🔍</span>
    <div class="rea-step-title">Retrieve Evidence</div>
    <div class="rea-step-desc">Query triggers ANN search across your vector store + Tavily web search. Cross-encoder reranker selects the top-5 most relevant chunks.</div>
  </div>
  <div class="rea-step-card">
    <span class="rea-step-num">Step 03</span>
    <span class="rea-step-emoji">📄</span>
    <div class="rea-step-title">Generate Report</div>
    <div class="rea-step-desc">Groq llama-3.3-70b runs a ReAct agent loop — Think → Act → Observe → Generate — producing a cited, structured executive report.</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Architecture strip ────────────────────────────────────────────────────────
st.markdown(section_label("SYSTEM ARCHITECTURE"), unsafe_allow_html=True)

st.markdown("""
<div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:var(--radius-xl);padding:1.75rem 2rem;margin-bottom:2rem;overflow-x:auto">
  <div style="display:flex;align-items:center;gap:0.5rem;min-width:600px">

    <div style="background:var(--bg-overlay);border:1px solid rgba(99,102,241,0.25);border-radius:10px;padding:0.875rem 1.25rem;flex:1;text-align:center">
      <div style="font-family:'Space Grotesk',sans-serif;font-size:0.625rem;font-weight:700;color:var(--indigo-400);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.25rem">Ingestion</div>
      <div style="font-size:0.8125rem;color:var(--text-secondary)">PDF · DOCX · XLSX<br><span style="color:var(--text-muted);font-size:0.75rem">→ Chunk → Embed → Store</span></div>
    </div>

    <div style="color:var(--text-muted);font-size:1.25rem;flex-shrink:0">→</div>

    <div style="background:var(--bg-overlay);border:1px solid rgba(16,185,129,0.2);border-radius:10px;padding:0.875rem 1.25rem;flex:1;text-align:center">
      <div style="font-family:'Space Grotesk',sans-serif;font-size:0.625rem;font-weight:700;color:var(--emerald);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.25rem">Retrieval</div>
      <div style="font-size:0.8125rem;color:var(--text-secondary)">ChromaDB ANN<br><span style="color:var(--text-muted);font-size:0.75rem">→ Rerank top-20 → top-5</span></div>
    </div>

    <div style="color:var(--text-muted);font-size:1.25rem;flex-shrink:0">→</div>

    <div style="background:var(--bg-overlay);border:1px solid rgba(245,158,11,0.2);border-radius:10px;padding:0.875rem 1.25rem;flex:1;text-align:center">
      <div style="font-family:'Space Grotesk',sans-serif;font-size:0.625rem;font-weight:700;color:var(--amber-500);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.25rem">ReAct Agent</div>
      <div style="font-size:0.8125rem;color:var(--text-secondary)">Groq llama-3.3-70b<br><span style="color:var(--text-muted);font-size:0.75rem">Think → Act → Observe</span></div>
    </div>

    <div style="color:var(--text-muted);font-size:1.25rem;flex-shrink:0">→</div>

    <div style="background:var(--bg-overlay);border:1px solid rgba(56,189,248,0.2);border-radius:10px;padding:0.875rem 1.25rem;flex:1;text-align:center">
      <div style="font-family:'Space Grotesk',sans-serif;font-size:0.625rem;font-weight:700;color:var(--sky);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.25rem">Delivery</div>
      <div style="font-size:0.8125rem;color:var(--text-secondary)">Cited Report<br><span style="color:var(--text-muted);font-size:0.75rem">DOCX · Markdown · API</span></div>
    </div>

  </div>
</div>
""", unsafe_allow_html=True)

# ── Stack pills ───────────────────────────────────────────────────────────────
st.markdown(section_label("FREE TIER STACK"), unsafe_allow_html=True)

stack = [
    ("🤖", "Groq", "llama-3.3-70b-versatile", "indigo"),
    ("🧠", "Embeddings", "all-MiniLM-L6-v2 (local)", "sky"),
    ("🗄️", "Vector DB", "ChromaDB (local disk)", "emerald"),
    ("🔁", "Reranker", "ms-marco-MiniLM (local)", "violet"),
    ("🌐", "Web Search", "Tavily API (1K/mo free)", "amber"),
    ("⚡", "Backend", "FastAPI + Uvicorn", "indigo"),
    ("🖥️", "Frontend", "Streamlit", "sky"),
    ("📝", "Export", "python-docx", "emerald"),
]

cols = st.columns(4)
for i, (icon, name, tech, color) in enumerate(stack):
    badge_map = {"indigo": "rea-badge-indigo", "amber": "rea-badge-amber",
                 "emerald": "rea-badge-emerald", "sky": "rea-badge-sky", "violet": "rea-badge-indigo"}
    with cols[i % 4]:
        st.markdown(f"""
<div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:var(--radius-lg);
     padding:1rem;margin-bottom:0.75rem;text-align:center">
  <div style="font-size:1.5rem;margin-bottom:0.5rem">{icon}</div>
  <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:0.875rem;
       color:var(--text-primary);margin-bottom:0.25rem">{name}</div>
  <div style="font-size:0.8rem;color:var(--text-muted)">{tech}</div>
</div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--border-subtle);
     display:flex;justify-content:space-between;align-items:center">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:0.8125rem;color:var(--text-muted)">
    RAG Executive Analyst · v1.0.0 · Portfolio Project
  </div>
  <div style="display:flex;gap:1rem">
    <span class="rea-badge rea-badge-emerald">✓ Free Tier</span>
    <span class="rea-badge rea-badge-indigo">Open Source</span>
  </div>
</div>
""", unsafe_allow_html=True)
