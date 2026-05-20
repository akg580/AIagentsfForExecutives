"""
frontend/pages/2_query.py
Natural language Q&A page with cited answers.
"""

import sys
from pathlib import Path

import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.components.theme import apply_enterprise_theme, render_sidebar

API = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Ask a Question", layout="wide")
apply_enterprise_theme()
render_sidebar()

st.title("Ask a Question")
st.caption("Ask business questions and receive cited answers grounded in your indexed data.")

with st.form("query_form"):
    query = st.text_area(
        "Your question",
        placeholder="Example: What are the key risks mentioned in the Q3 board report?",
        height=100,
    )

    col1, col2, col3 = st.columns(3)
    search_mode = col1.selectbox(
        "Search mode",
        ["hybrid", "internal", "web"],
        help="Hybrid combines internal documents with web context.",
    )
    top_k = col2.slider("Sources to retrieve", min_value=1, max_value=10, value=5)
    show_trace = col3.checkbox("Show reasoning trace", value=False)

    submitted = st.form_submit_button("Search", type="primary", use_container_width=True)

if submitted and query.strip():
    with st.spinner("Retrieving evidence and generating answer..."):
        try:
            response = requests.post(
                f"{API}/query",
                json={
                    "query": query,
                    "search_mode": search_mode,
                    "top_k": top_k,
                    "include_trace": show_trace,
                },
                timeout=90,
            )

            if response.status_code == 200:
                data = response.json()

                st.markdown("### Answer")
                st.markdown(data["answer"])

                m1, m2, m3 = st.columns(3)
                m1.metric("Response Time", f"{data['latency_ms']:.0f} ms")
                m2.metric("Sources Used", len(data["sources"]))
                m3.metric("Search Mode", data["search_mode"])

                st.markdown("---")
                st.markdown("### Sources")
                for i, src in enumerate(data["sources"], 1):
                    location = (
                        f"Page {src['page']}" if src["source_type"] == "internal" else src.get("url", "Web")
                    )
                    with st.expander(
                        f"[SOURCE {i}] {src['filename']} | {location} | Score: {src['score']:.3f}",
                        expanded=i <= 2,
                    ):
                        source_label = "Web" if src["source_type"] == "web" else "Internal"
                        st.caption(f"Source Type: {source_label}")
                        st.markdown(src["content"])
                        if src.get("url"):
                            st.markdown(f"[Read full article]({src['url']})")

                if show_trace and data.get("trace"):
                    st.markdown("---")
                    st.markdown("### Agent Reasoning Trace")
                    for step in data["trace"]:
                        st.markdown(f"**{step['step']}:** {step['content']}")

            else:
                st.error(f"Query failed: {response.json().get('detail', 'Unknown error')}")

        except requests.Timeout:
            st.error("Query timed out. Backend may be busy; try again or reduce scope.")
        except requests.ConnectionError:
            st.error("Backend offline. Run: `uvicorn backend.main:app --reload --port 8000`")

elif submitted:
    st.warning("Please enter a question.")
