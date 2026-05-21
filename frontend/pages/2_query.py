"""
frontend/pages/2_query.py
──────────────────────────
Enterprise Q&A interface — cited answers from your documents.
"""
import streamlit as st
import requests
from frontend.components.styles import (
    get_css, sidebar_html, page_header, section_label,
    source_card, answer_block, trace_step
)

API = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Ask · RAG Analyst", page_icon="🔍", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(sidebar_html(), unsafe_allow_html=True)
    st.markdown('<div class="rea-sidebar-section">Navigation</div>', unsafe_allow_html=True)
    for icon, label, active in [("🏠","Home",False),("📁","Upload Documents",False),("🔍","Ask a Question",True),("📄","Generate Report",False)]:
        cls = "active" if active else ""
        st.markdown(f'<div class="rea-nav-item {cls}">{icon}&nbsp;&nbsp;{label}</div>', unsafe_allow_html=True)

    st.markdown('<div class="rea-sidebar-section">Settings</div>', unsafe_allow_html=True)
    search_mode = st.selectbox("Search Mode", ["hybrid", "internal", "web"], index=0,
                               help="Hybrid = your docs + live web. Recommended.")
    top_k       = st.slider("Evidence chunks", 1, 10, 5)
    show_trace  = st.checkbox("Show agent trace", value=False)

    st.markdown('<div class="rea-sidebar-section">Examples</div>', unsafe_allow_html=True)
    examples = [
        "What are the key risk factors in the uploaded report?",
        "Summarise the main financial metrics from Q3.",
        "What competitive threats are mentioned across documents?",
        "What are the strategic priorities for the next 12 months?",
    ]
    for ex in examples:
        if st.button(ex[:45] + "…", key=ex, use_container_width=True):
            st.session_state["prefill_query"] = ex

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(page_header(
    title="Ask a Question",
    subtitle="Get cited, evidence-grounded answers from your indexed documents and the live web — in under 5 seconds.",
    badge="🔍 Semantic Search",
    badge_type="indigo",
), unsafe_allow_html=True)

# ── Query input ───────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill_query", "")

with st.form("query_form", clear_on_submit=False):
    query = st.text_area(
        "Your question",
        value=prefill,
        placeholder="e.g. What are the key risks mentioned in the board report? What was the revenue in Q3?",
        height=90,
        label_visibility="collapsed",
    )

    col_sub, col_mode, col_k, col_trace = st.columns([3, 2, 2, 2])
    submitted = col_sub.form_submit_button("🔍  Search", type="primary", use_container_width=True)
    col_mode.markdown(f"""
<div style="padding:0.5rem 0;font-size:0.8rem;color:var(--text-muted)">
  Mode: <strong style="color:var(--indigo-400)">{search_mode}</strong>
</div>""", unsafe_allow_html=True)
    col_k.markdown(f"""
<div style="padding:0.5rem 0;font-size:0.8rem;color:var(--text-muted)">
  Evidence: <strong style="color:var(--indigo-400)">{top_k} chunks</strong>
</div>""", unsafe_allow_html=True)
    col_trace.markdown(f"""
<div style="padding:0.5rem 0;font-size:0.8rem;color:var(--text-muted)">
  Trace: <strong style="color:var(--indigo-400)">{'On' if show_trace else 'Off'}</strong>
</div>""", unsafe_allow_html=True)

# ── Results ───────────────────────────────────────────────────────────────────
if submitted and query.strip():
    with st.spinner("Retrieving evidence and generating answer…"):
        try:
            response = requests.post(
                f"{API}/query",
                json={"query": query, "search_mode": search_mode, "top_k": top_k, "include_trace": show_trace},
                timeout=60,
            )

            if response.status_code == 200:
                data = response.json()

                # ── Answer ────────────────────────────────────────────────────
                st.markdown(section_label("ANSWER"), unsafe_allow_html=True)
                st.markdown(answer_block(data["answer"]), unsafe_allow_html=True)

                # ── Metrics strip ─────────────────────────────────────────────
                srcs = data.get("sources", [])
                internal_count = sum(1 for s in srcs if s.get("source_type") == "internal")
                web_count      = sum(1 for s in srcs if s.get("source_type") == "web")
                lat = data.get("latency_ms", 0)

                st.markdown(f"""
<div style="display:flex;gap:1.5rem;padding:0.875rem 1.25rem;
     background:var(--bg-elevated);border:1px solid var(--border-subtle);
     border-radius:var(--radius-lg);margin-bottom:1.5rem">
  <div>
    <div style="font-size:0.675rem;text-transform:uppercase;letter-spacing:0.08em;
         color:var(--text-muted);font-family:'Space Grotesk',sans-serif;font-weight:600">Response Time</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.125rem;font-weight:700;
         color:var(--emerald)">{lat:.0f} ms</div>
  </div>
  <div style="width:1px;background:var(--border-subtle)"></div>
  <div>
    <div style="font-size:0.675rem;text-transform:uppercase;letter-spacing:0.08em;
         color:var(--text-muted);font-family:'Space Grotesk',sans-serif;font-weight:600">Internal Sources</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.125rem;font-weight:700;
         color:var(--indigo-400)">{internal_count}</div>
  </div>
  <div style="width:1px;background:var(--border-subtle)"></div>
  <div>
    <div style="font-size:0.675rem;text-transform:uppercase;letter-spacing:0.08em;
         color:var(--text-muted);font-family:'Space Grotesk',sans-serif;font-weight:600">Web Sources</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.125rem;font-weight:700;
         color:var(--sky)">{web_count}</div>
  </div>
  <div style="width:1px;background:var(--border-subtle)"></div>
  <div>
    <div style="font-size:0.675rem;text-transform:uppercase;letter-spacing:0.08em;
         color:var(--text-muted);font-family:'Space Grotesk',sans-serif;font-weight:600">Mode</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.125rem;font-weight:700;
         color:var(--amber-500)">{data.get('search_mode','—').title()}</div>
  </div>
</div>
""", unsafe_allow_html=True)

                # ── Sources ───────────────────────────────────────────────────
                if srcs:
                    st.markdown(section_label("EVIDENCE SOURCES"), unsafe_allow_html=True)

                    # Two-column: internal left, web right
                    internal_srcs = [s for s in srcs if s.get("source_type") == "internal"]
                    web_srcs      = [s for s in srcs if s.get("source_type") == "web"]

                    if internal_srcs and web_srcs:
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f'<div class="rea-badge rea-badge-indigo">📄 Internal · {len(internal_srcs)}</div>', unsafe_allow_html=True)
                            for i, s in enumerate(internal_srcs, 1):
                                with st.expander(f"{s['filename']} — p.{s['page']} (score {s['score']:.2f})", expanded=i==1):
                                    st.markdown(f"<div style='font-size:0.875rem;color:var(--text-secondary);line-height:1.7'>{s['content']}</div>", unsafe_allow_html=True)
                        with c2:
                            st.markdown(f'<div class="rea-badge rea-badge-sky">🌐 Web · {len(web_srcs)}</div>', unsafe_allow_html=True)
                            for i, s in enumerate(web_srcs, 1):
                                with st.expander(f"{s['filename'][:50]} (score {s['score']:.2f})", expanded=i==1):
                                    st.markdown(f"<div style='font-size:0.875rem;color:var(--text-secondary);line-height:1.7'>{s['content']}</div>", unsafe_allow_html=True)
                                    if s.get("url"):
                                        st.markdown(f"[↗ Read full article]({s['url']})")
                    else:
                        # Single column
                        all_displayed = internal_srcs or web_srcs
                        for i, s in enumerate(all_displayed, 1):
                            badge_type = "internal" if s.get("source_type") == "internal" else "web"
                            meta = f"Page {s['page']}" if badge_type == "internal" else (s.get("url", "")[:60])
                            st.markdown(source_card(i, s["filename"], meta, s["score"], s["content"], s.get("url","")), unsafe_allow_html=True)

                # ── Trace ─────────────────────────────────────────────────────
                if show_trace and data.get("trace"):
                    st.markdown(section_label("AGENT REASONING TRACE"), unsafe_allow_html=True)
                    st.markdown('<div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:var(--radius-lg);padding:1.25rem 1.5rem">', unsafe_allow_html=True)
                    for step in data["trace"]:
                        st.markdown(trace_step(step["step"], step["content"]), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            elif response.status_code == 422:
                st.error("Please upload at least one document before querying.")
            else:
                st.error(f"Query failed: {response.json().get('detail', 'Unknown error')}")

        except requests.ConnectionError:
            st.error("❌ Backend offline — run: `uvicorn backend.main:app --reload --port 8000`")

elif submitted:
    st.warning("Please enter a question above.")

# ── Empty state ───────────────────────────────────────────────────────────────
elif not prefill:
    st.markdown("""
<div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:var(--radius-xl);
     padding:3.5rem;text-align:center;margin-top:1.5rem">
  <div style="font-size:3rem;margin-bottom:1rem">🔍</div>
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.125rem;font-weight:700;
       color:var(--text-secondary);margin-bottom:0.5rem">Ask anything about your documents</div>
  <div style="font-size:0.9rem;color:var(--text-muted);max-width:480px;margin:0 auto;line-height:1.7">
    Type a question above or pick an example from the sidebar. The AI will retrieve relevant passages
    from your indexed documents and the web, then generate a cited answer.
  </div>
</div>
""", unsafe_allow_html=True)
