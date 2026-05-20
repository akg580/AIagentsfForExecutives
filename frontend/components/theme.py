"""
frontend/components/theme.py
Shared UI theme utilities for Streamlit pages.
"""

import streamlit as st


def apply_enterprise_theme() -> None:
    st.markdown(
        """
<style>
    :root {
        --bg: #f4f7fb;
        --panel: #ffffff;
        --ink: #0f172a;
        --muted: #475569;
        --line: #dbe3ef;
        --brand: #1f3f75;
        --brand-soft: #e8eef9;
    }

    .stApp {
        background: linear-gradient(180deg, #f7f9fc 0%, #eef3fa 100%);
    }

    [data-testid="stSidebar"] {
        background: #102a52;
        border-right: 1px solid #1d3b68;
    }

    [data-testid="stSidebar"] * {
        color: #eef4ff !important;
    }

    [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 10px 14px;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    textarea {
        border-radius: 8px !important;
        border-color: #c4d1e4 !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 8px !important;
        border: 1px solid #c4d1e4 !important;
        font-weight: 600 !important;
        letter-spacing: 0.1px;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
</style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### RAG Executive Analyst")
        st.caption("Enterprise Research Workspace")
        st.markdown("---")
        st.markdown("**Navigation**")
        st.page_link("app.py", label="Home")
        st.page_link("pages/1_upload.py", label="Upload Documents")
        st.page_link("pages/2_query.py", label="Ask a Question")
        st.page_link("pages/3_reports.py", label="Generate Report")
        st.markdown("---")
        st.markdown("**Backend**")
        st.markdown("[API Docs](http://localhost:8000/docs)")
        st.markdown("[Health Check](http://localhost:8000/api/v1/health)")
        st.markdown("---")
        st.markdown("**Stack**")
        st.caption("Groq LLM")
        st.caption("ChromaDB")
        st.caption("Tavily Search")
        st.caption("all-MiniLM-L6-v2")
