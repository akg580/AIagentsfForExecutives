"""
frontend/app.py
Streamlit main entry point.
Run with: streamlit run frontend/app.py
"""

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.components.theme import apply_enterprise_theme, render_sidebar

st.set_page_config(
    page_title="RAG Executive Analyst",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_enterprise_theme()
render_sidebar()

st.title("RAG Executive Analyst")
st.subheader("AI-Powered Business Intelligence Platform")
st.markdown(
    "Upload internal documents, ask questions in natural language, and generate structured "
    "executive reports grounded in your data with citations."
)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Generation Time", "< 60 sec", delta="Target")
col2.metric("Retrieval Accuracy", "85%+ MRR", delta="Reranked")
col3.metric("Citation Rate", "100%", delta="Hard Gate")
col4.metric("Infra Cost", "$0 / month", delta="Free Tier")

st.markdown("---")
st.markdown("### Workflow")

c1, c2, c3 = st.columns(3)
with c1:
    st.info("**Step 1: Upload Documents**\n\nIndex PDF, DOCX, XLSX, TXT, or Markdown files.")
with c2:
    st.info("**Step 2: Ask Questions**\n\nRun evidence-grounded retrieval and generate cited answers.")
with c3:
    st.info("**Step 3: Generate Reports**\n\nProduce enterprise-ready reports with downloadable exports.")

st.markdown("---")
st.caption("RAG Executive Analyst v1.0 | Groq + ChromaDB + Tavily")
