"""
frontend/pages/3_reports.py
Executive report generation page with DOCX export.
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

SECTION_OPTIONS = {
    "executive_summary": "Executive Summary",
    "key_findings": "Key Findings",
    "data_table": "Data and Metrics Table",
    "market_context": "Market Context",
    "risk_factors": "Risk Factors",
    "recommendations": "Recommendations",
}

st.set_page_config(page_title="Generate Report", layout="wide")
apply_enterprise_theme()
render_sidebar()

st.title("Generate Executive Report")
st.caption("Generate a structured report grounded in indexed documents with transparent sourcing.")

with st.form("report_form"):
    report_title = st.text_input(
        "Report title",
        placeholder="Example: Q3 2025 Competitor Intelligence Report",
    )

    research_query = st.text_area(
        "Research question or focus",
        placeholder=(
            "Example: Analyze the competitive landscape in the Indian fintech sector, "
            "focusing on funding trends, key players, and regulatory risks in 2025."
        ),
        height=120,
    )

    col1, col2 = st.columns(2)

    search_mode = col1.selectbox(
        "Search mode",
        ["hybrid", "internal", "web"],
        help="Hybrid combines indexed documents with live web context.",
    )

    selected_sections = col2.multiselect(
        "Report sections",
        options=list(SECTION_OPTIONS.keys()),
        default=["executive_summary", "key_findings", "market_context", "risk_factors", "recommendations"],
        format_func=lambda x: SECTION_OPTIONS[x],
    )

    include_trace = st.checkbox("Include agent reasoning trace", value=False)

    generate_btn = st.form_submit_button("Generate Report", type="primary", use_container_width=True)

if generate_btn:
    if not report_title.strip():
        st.warning("Please enter a report title.")
    elif not research_query.strip():
        st.warning("Please enter a research question.")
    elif not selected_sections:
        st.warning("Please select at least one section.")
    else:
        progress = st.progress(0, "Starting report generation...")

        with st.spinner(f"Generating '{report_title}'... This may take 30 to 60 seconds."):
            try:
                progress.progress(20, "Retrieving evidence from documents...")
                response = requests.post(
                    f"{API}/reports/generate",
                    json={
                        "title": report_title,
                        "query": research_query,
                        "search_mode": search_mode,
                        "sections": selected_sections,
                        "include_trace": include_trace,
                    },
                    timeout=180,
                )
                progress.progress(90, "Finalizing report...")

                if response.status_code == 200:
                    data = response.json()
                    progress.progress(100, "Report ready")

                    st.markdown(f"## {data['title']}")
                    st.caption(
                        f"Generated in {data['latency_ms']:.0f} ms | "
                        f"{len(data['all_sources'])} sources | "
                        f"{len(data['sections'])} sections"
                    )

                    ex1, ex2 = st.columns(2)

                    docx_resp = requests.get(
                        f"{API}/reports/{data['report_id']}/export?format=docx",
                        timeout=60,
                    )
                    if docx_resp.status_code == 200:
                        ex1.download_button(
                            "Download DOCX",
                            data=docx_resp.content,
                            file_name=f"{report_title[:40]}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary",
                            use_container_width=True,
                        )

                    md_resp = requests.get(
                        f"{API}/reports/{data['report_id']}/export?format=markdown",
                        timeout=60,
                    )
                    if md_resp.status_code == 200:
                        ex2.download_button(
                            "Download Markdown",
                            data=md_resp.content,
                            file_name=f"{report_title[:40]}.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )

                    st.divider()

                    for section in data["sections"]:
                        st.markdown(f"### {section['section']}")
                        st.markdown(section["content"])
                        st.markdown("")

                    st.divider()
                    st.markdown("### All Sources")
                    sources = data.get("all_sources", [])

                    seen = set()
                    unique = []
                    for source in sources:
                        key = source.get("url") or f"{source.get('filename')}:{source.get('page')}"
                        if key not in seen:
                            seen.add(key)
                            unique.append(source)

                    for i, source in enumerate(unique, 1):
                        if source["source_type"] == "web":
                            label = f"[SOURCE {i}] {source.get('filename', 'Web')} | [link]({source.get('url', '')})"
                        else:
                            label = (
                                f"[SOURCE {i}] {source.get('filename', '?')} | "
                                f"Page {source.get('page', '?')} | Score: {source.get('score', 0):.3f}"
                            )
                        st.caption(label)

                    if include_trace and data.get("trace"):
                        st.divider()
                        st.markdown("### Agent Reasoning Trace")
                        for step in data["trace"]:
                            st.markdown(f"**{step['step']}:** {step['content']}")

                elif response.status_code == 422:
                    progress.empty()
                    st.error(
                        f"{response.json().get('detail', 'Validation error')}\n\n"
                        "Please upload documents before generating a report."
                    )
                else:
                    progress.empty()
                    st.error(f"Generation failed: {response.json().get('detail', 'Unknown error')}")

            except requests.Timeout:
                progress.empty()
                st.error("Report request timed out. Try fewer sections or a narrower query.")
            except requests.ConnectionError:
                progress.empty()
                st.error("Backend offline. Run: `uvicorn backend.main:app --reload --port 8000`")
