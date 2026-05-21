"""
frontend/pages/3_reports.py
────────────────────────────
Enterprise report generator with DOCX/Markdown export.
"""
import streamlit as st
import requests
from frontend.components.styles import (
    get_css, sidebar_html, page_header, section_label,
    report_section_card, trace_step
)

API = "http://localhost:8000/api/v1"

SECTION_OPTIONS = {
    "executive_summary": ("📋", "Executive Summary",  "3–5 sentence synthesis"),
    "key_findings":      ("🔑", "Key Findings",        "5–7 evidence-backed insights"),
    "data_table":        ("📊", "Data & Metrics",      "Quantitative comparison table"),
    "market_context":    ("🌐", "Market Context",      "Industry trends + benchmarks"),
    "risk_factors":      ("⚠️", "Risk Factors",        "Ranked risks with likelihood"),
    "recommendations":   ("✅", "Recommendations",     "Actionable next steps"),
}

SECTION_ICONS = {k: v[0] for k, v in SECTION_OPTIONS.items()}

st.set_page_config(page_title="Reports · RAG Analyst", page_icon="📄", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(sidebar_html(), unsafe_allow_html=True)
    st.markdown('<div class="rea-sidebar-section">Navigation</div>', unsafe_allow_html=True)
    for icon, label, active in [("🏠","Home",False),("📁","Upload Documents",False),("🔍","Ask a Question",False),("📄","Generate Report",True)]:
        cls = "active" if active else ""
        st.markdown(f'<div class="rea-nav-item {cls}">{icon}&nbsp;&nbsp;{label}</div>', unsafe_allow_html=True)

    st.markdown('<div class="rea-sidebar-section">Report Config</div>', unsafe_allow_html=True)
    search_mode = st.selectbox("Search Mode", ["hybrid", "internal", "web"], index=0)

    st.markdown("**Sections to include**")
    selected_sections = []
    for key, (icon, label, desc) in SECTION_OPTIONS.items():
        default = key in ["executive_summary", "key_findings", "market_context", "risk_factors", "recommendations"]
        if st.checkbox(f"{icon} {label}", value=default, key=f"sec_{key}"):
            selected_sections.append(key)

    include_trace = st.checkbox("Include reasoning trace", value=False)

    st.markdown('<div class="rea-sidebar-section">Info</div>', unsafe_allow_html=True)
    st.markdown("""
<div style="padding:0.75rem;background:var(--amber-glow);border:1px solid rgba(245,158,11,0.2);
     border-radius:10px;margin:0 0.5rem">
  <div style="font-size:0.8rem;color:var(--text-muted);line-height:1.6">
    ⏱ Report generation takes <strong style="color:var(--amber-500)">30–60 seconds</strong>.
    Each section makes a separate Groq API call.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(page_header(
    title="Generate Executive Report",
    subtitle="Define a research question. The AI retrieves evidence, runs a ReAct agent loop, and generates a structured, cited report — exportable as DOCX.",
    badge="📄 Report Engine",
    badge_type="amber",
), unsafe_allow_html=True)

# ── Report form ───────────────────────────────────────────────────────────────
st.markdown(section_label("REPORT CONFIGURATION"), unsafe_allow_html=True)

with st.form("report_form"):
    col_t, col_q = st.columns([1, 2])

    with col_t:
        report_title = st.text_input(
            "Report Title",
            placeholder="e.g. Q3 2025 Competitor Intelligence",
        )

    with col_q:
        research_query = st.text_area(
            "Research Question",
            placeholder="e.g. Analyse the competitive landscape in the Indian fintech sector, focusing on funding trends, key players, and regulatory risks in 2025.",
            height=70,
        )

    # Section preview chips
    if selected_sections:
        chips = " ".join([
            f'<span class="rea-badge rea-badge-indigo">{SECTION_OPTIONS[s][0]} {SECTION_OPTIONS[s][1]}</span>'
            for s in selected_sections
        ])
        st.markdown(f'<div style="margin:0.5rem 0">{chips}</div>', unsafe_allow_html=True)

    generate_btn = st.form_submit_button("🚀  Generate Report", type="primary", use_container_width=True)

# ── Generation ────────────────────────────────────────────────────────────────
if generate_btn:
    errors = []
    if not report_title.strip():
        errors.append("Report title is required.")
    if not research_query.strip():
        errors.append("Research question is required.")
    if not selected_sections:
        errors.append("Select at least one report section.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        # Progress stages
        stages = [
            (10, "Initialising ReAct agent loop…"),
            (25, "Retrieving evidence from vector store…"),
            (45, "Running Tavily web search for market context…"),
            (60, "Generating Executive Summary…"),
            (75, "Generating Key Findings & Data Table…"),
            (88, "Generating Risks & Recommendations…"),
            (96, "Assembling report and validating citations…"),
        ]

        prog = st.progress(0, stages[0][1])

        import time
        with st.spinner(""):
            try:
                # Show animated progress while waiting
                for pct, msg in stages[:3]:
                    prog.progress(pct, msg)
                    time.sleep(0.4)

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

                for pct, msg in stages[3:]:
                    prog.progress(pct, msg)
                    time.sleep(0.25)

                prog.progress(100, "✓ Report ready!")

                if response.status_code == 200:
                    data = response.json()

                    # ── Report header ──────────────────────────────────────────
                    lat = data.get("latency_ms", 0)
                    n_src = len(data.get("all_sources", []))
                    n_sec = len(data.get("sections", []))

                    st.markdown(f"""
<div style="background:linear-gradient(135deg,#0D1321,#111827);border:1px solid var(--border-default);
     border-radius:var(--radius-xl);padding:2rem 2.5rem;margin:1.5rem 0;position:relative;overflow:hidden">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
       background:linear-gradient(90deg,var(--indigo-600),var(--amber-500),var(--emerald))"></div>
  <div class="rea-badge rea-badge-emerald" style="margin-bottom:0.75rem">✓ Report Generated</div>
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.5rem;font-weight:700;
       color:var(--text-primary);letter-spacing:-0.025em;margin-bottom:0.5rem">{data['title']}</div>
  <div style="font-size:0.875rem;color:var(--text-muted);margin-bottom:1.5rem">{data['query'][:120]}{"…" if len(data['query'])>120 else ""}</div>
  <div style="display:flex;gap:2rem">
    <div><span style="font-family:'Space Grotesk',sans-serif;font-size:1.25rem;font-weight:700;color:var(--emerald)">{lat:.0f}ms</span>
         <span style="font-size:0.8rem;color:var(--text-muted);margin-left:0.375rem">generation time</span></div>
    <div><span style="font-family:'Space Grotesk',sans-serif;font-size:1.25rem;font-weight:700;color:var(--indigo-400)">{n_src}</span>
         <span style="font-size:0.8rem;color:var(--text-muted);margin-left:0.375rem">sources used</span></div>
    <div><span style="font-family:'Space Grotesk',sans-serif;font-size:1.25rem;font-weight:700;color:var(--amber-500)">{n_sec}</span>
         <span style="font-size:0.8rem;color:var(--text-muted);margin-left:0.375rem">sections</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

                    # ── Export buttons ─────────────────────────────────────────
                    st.markdown(section_label("EXPORT REPORT"), unsafe_allow_html=True)
                    ex1, ex2, ex3 = st.columns(3)

                    docx_resp = requests.get(f"{API}/reports/{data['report_id']}/export?format=docx", timeout=30)
                    if docx_resp.status_code == 200:
                        ex1.download_button(
                            "⬇️  Download DOCX",
                            data=docx_resp.content,
                            file_name=f"{report_title[:40]}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            type="primary", use_container_width=True,
                        )

                    md_resp = requests.get(f"{API}/reports/{data['report_id']}/export?format=markdown", timeout=30)
                    if md_resp.status_code == 200:
                        ex2.download_button(
                            "⬇️  Download Markdown",
                            data=md_resp.content,
                            file_name=f"{report_title[:40]}.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )

                    ex3.markdown(f"""
<div style="padding:0.6rem;text-align:center;font-size:0.8rem;color:var(--text-muted)">
  Report ID:<br>
  <code style="font-family:'Space Grotesk',sans-serif;font-size:0.75rem;
       color:var(--indigo-400);background:var(--indigo-glow);padding:2px 8px;border-radius:4px">
  {data['report_id'][:20]}…
  </code>
</div>""", unsafe_allow_html=True)

                    # ── Report sections ────────────────────────────────────────
                    st.markdown(section_label("REPORT CONTENT"), unsafe_allow_html=True)

                    for section in data.get("sections", []):
                        key = section.get("section_key", "")
                        icon = SECTION_ICONS.get(key, "📋")
                        st.markdown(
                            report_section_card(section["section"], icon, section["content"]),
                            unsafe_allow_html=True,
                        )

                    # ── Source reference list ──────────────────────────────────
                    st.markdown(section_label("REFERENCES"), unsafe_allow_html=True)

                    seen = set()
                    unique_sources = []
                    for s in data.get("all_sources", []):
                        k = s.get("url") or f"{s.get('filename')}:{s.get('page')}"
                        if k not in seen:
                            seen.add(k)
                            unique_sources.append(s)

                    refs_html = ""
                    for i, s in enumerate(unique_sources, 1):
                        if s.get("source_type") == "web":
                            url = s.get("url", "")
                            refs_html += f"""
<div style="display:flex;gap:0.75rem;padding:0.5rem 0;border-bottom:1px solid var(--border-subtle);
     align-items:baseline">
  <span style="font-family:'Space Grotesk',sans-serif;font-size:0.75rem;font-weight:700;
       color:var(--sky);min-width:28px">[{i}]</span>
  <span style="font-size:0.85rem;color:var(--text-secondary)">🌐 {s.get('filename','Web')} — <a href="{url}" target="_blank" style="color:var(--sky)">{url[:70]}</a></span>
  <span style="font-family:'Space Grotesk',sans-serif;font-size:0.7rem;color:var(--text-muted);margin-left:auto">score {s.get('score',0):.2f}</span>
</div>"""
                        else:
                            refs_html += f"""
<div style="display:flex;gap:0.75rem;padding:0.5rem 0;border-bottom:1px solid var(--border-subtle);
     align-items:baseline">
  <span style="font-family:'Space Grotesk',sans-serif;font-size:0.75rem;font-weight:700;
       color:var(--indigo-400);min-width:28px">[{i}]</span>
  <span style="font-size:0.85rem;color:var(--text-secondary)">📄 {s.get('filename','?')} — Page {s.get('page','?')}</span>
  <span style="font-family:'Space Grotesk',sans-serif;font-size:0.7rem;color:var(--text-muted);margin-left:auto">score {s.get('score',0):.2f}</span>
</div>"""

                    st.markdown(f"""
<div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);
     border-radius:var(--radius-lg);padding:1.25rem 1.5rem">{refs_html}</div>
""", unsafe_allow_html=True)

                    # ── Trace ──────────────────────────────────────────────────
                    if include_trace and data.get("trace"):
                        st.markdown(section_label("AGENT REASONING TRACE"), unsafe_allow_html=True)
                        st.markdown('<div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:var(--radius-lg);padding:1.25rem 1.5rem">', unsafe_allow_html=True)
                        for step in data["trace"]:
                            st.markdown(trace_step(step["step"], step["content"]), unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                elif response.status_code == 422:
                    prog.empty()
                    err = response.json().get("detail", "")
                    st.markdown(f"""
<div style="background:var(--amber-glow);border:1px solid rgba(245,158,11,0.3);border-radius:var(--radius-lg);padding:1.25rem 1.5rem">
  <div style="font-weight:700;color:var(--amber-500);margin-bottom:0.375rem">⚠ Cannot Generate Report</div>
  <div style="font-size:0.875rem;color:var(--text-muted)">{err or 'No documents indexed. Upload documents first in the Documents page.'}</div>
</div>""", unsafe_allow_html=True)
                else:
                    prog.empty()
                    st.error(f"Generation failed: {response.json().get('detail','Unknown error')}")

            except requests.ConnectionError:
                prog.empty()
                st.error("❌ Backend offline — run: `uvicorn backend.main:app --reload --port 8000`")
            except requests.Timeout:
                prog.empty()
                st.error("⏱ Request timed out. Try with fewer sections or a narrower query.")

# ── Empty state ───────────────────────────────────────────────────────────────
elif not generate_btn:
    st.markdown("""
<div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:var(--radius-xl);
     padding:3.5rem;text-align:center;margin-top:1rem">
  <div style="font-size:3rem;margin-bottom:1rem">📄</div>
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.125rem;font-weight:700;
       color:var(--text-secondary);margin-bottom:0.5rem">Configure your report above</div>
  <div style="font-size:0.9rem;color:var(--text-muted);max-width:520px;margin:0 auto;line-height:1.7">
    Enter a title and research question, choose your sections in the sidebar,
    then click <strong style="color:var(--indigo-400)">Generate Report</strong>.
    The AI will retrieve evidence from your documents and the web,
    then produce a structured, cited executive report ready for export.
  </div>
  <div style="margin-top:2rem;display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap">
    <span class="rea-badge rea-badge-indigo">📋 Executive Summary</span>
    <span class="rea-badge rea-badge-amber">🔑 Key Findings</span>
    <span class="rea-badge rea-badge-sky">🌐 Market Context</span>
    <span class="rea-badge rea-badge-emerald">✅ Recommendations</span>
  </div>
</div>
""", unsafe_allow_html=True)
