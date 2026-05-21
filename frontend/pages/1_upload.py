"""
frontend/pages/1_upload.py
───────────────────────────
Enterprise document management page.
"""
import streamlit as st
import requests
from frontend.components.styles import (
    get_css, sidebar_html, page_header, section_label, doc_row
)

API = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Documents · RAG Analyst", page_icon="📁", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(sidebar_html(), unsafe_allow_html=True)
    st.markdown('<div class="rea-sidebar-section">Navigation</div>', unsafe_allow_html=True)
    nav = [("🏠","Home",False),("📁","Upload Documents",True),("🔍","Ask a Question",False),("📄","Generate Report",False)]
    for icon, label, active in nav:
        cls = "active" if active else ""
        st.markdown(f'<div class="rea-nav-item {cls}">{icon}&nbsp;&nbsp;{label}</div>', unsafe_allow_html=True)

    st.markdown('<div class="rea-sidebar-section">Tips</div>', unsafe_allow_html=True)
    st.markdown("""
<div style="padding:0.75rem;background:var(--indigo-glow);border:1px solid rgba(99,102,241,0.2);
     border-radius:10px;margin:0 0.5rem">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:0.75rem;font-weight:600;
       color:var(--indigo-400);margin-bottom:0.375rem">Best results</div>
  <div style="font-size:0.8rem;color:var(--text-muted);line-height:1.6">
    Upload 3–5 related documents (annual reports, board decks, research papers) for richer cross-document synthesis.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(page_header(
    title="Document Management",
    subtitle="Upload, index, and manage your internal documents. Supports PDF, DOCX, XLSX, TXT, and Markdown.",
    badge="📁 Knowledge Base",
    badge_type="sky",
), unsafe_allow_html=True)

# ── Upload zone ───────────────────────────────────────────────────────────────
st.markdown(section_label("UPLOAD NEW DOCUMENT"), unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drop a file or click to browse",
    type=["pdf", "docx", "doc", "xlsx", "xls", "txt", "md"],
    label_visibility="collapsed",
)

if uploaded:
    # File preview card
    size_kb = uploaded.size / 1024
    size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
    ext = uploaded.name.rsplit(".", 1)[-1].upper() if "." in uploaded.name else "FILE"

    st.markdown(f"""
<div style="background:var(--bg-elevated);border:1px solid var(--border-default);border-radius:var(--radius-lg);
     padding:1.25rem 1.5rem;display:flex;align-items:center;gap:1.25rem;margin:1rem 0">
  <div style="width:44px;height:44px;background:var(--indigo-glow);border:1px solid rgba(99,102,241,0.3);
       border-radius:10px;display:flex;align-items:center;justify-content:center;
       font-family:'Space Grotesk',sans-serif;font-size:0.6875rem;font-weight:700;
       color:var(--indigo-400)">{ext}</div>
  <div style="flex:1">
    <div style="font-weight:600;font-size:0.9375rem;color:var(--text-primary);margin-bottom:0.2rem">{uploaded.name}</div>
    <div style="font-size:0.8125rem;color:var(--text-muted)">{size_str} · Ready to index</div>
  </div>
  <span class="rea-badge rea-badge-amber">Pending</span>
</div>
""", unsafe_allow_html=True)

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        do_upload = st.button("⬆️ Index Document", type="primary", use_container_width=True)

    if do_upload:
        prog = st.progress(0, "Uploading file...")
        with st.spinner(""):
            try:
                prog.progress(20, "Chunking text into segments...")
                response = requests.post(
                    f"{API}/documents/upload",
                    files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")},
                    timeout=120,
                )
                prog.progress(70, "Generating embeddings...")
                prog.progress(95, "Writing to vector store...")

                if response.status_code == 201:
                    data = response.json()
                    prog.progress(100, "Done!")
                    st.markdown(f"""
<div style="background:var(--emerald-dim);border:1px solid rgba(16,185,129,0.25);border-radius:var(--radius-lg);
     padding:1.25rem 1.5rem;margin-top:1rem">
  <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;color:var(--emerald);font-size:1rem;margin-bottom:0.5rem">
    ✓ Successfully Indexed
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.75rem;margin-top:0.75rem">
    <div><div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;
         font-family:'Space Grotesk',sans-serif;font-weight:600">Chunks Created</div>
         <div style="font-family:'Space Grotesk',sans-serif;font-size:1.25rem;font-weight:700;
         color:var(--text-primary)">{data['chunk_count']}</div></div>
    <div><div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;
         font-family:'Space Grotesk',sans-serif;font-weight:600">File</div>
         <div style="font-size:0.875rem;font-weight:600;color:var(--text-primary)">{data['filename']}</div></div>
    <div><div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.06em;
         font-family:'Space Grotesk',sans-serif;font-weight:600">Doc ID</div>
         <div style="font-size:0.75rem;color:var(--text-muted);font-family:'Space Grotesk',sans-serif">{data['doc_id'][:16]}…</div></div>
  </div>
</div>
""", unsafe_allow_html=True)
                else:
                    prog.empty()
                    err = response.json().get("detail", "Unknown error")
                    st.error(f"Upload failed: {err}")

            except requests.ConnectionError:
                prog.empty()
                st.error("❌ Backend offline — run: `uvicorn backend.main:app --reload --port 8000`")

# ── Document library ──────────────────────────────────────────────────────────
st.markdown(section_label("INDEXED DOCUMENTS"), unsafe_allow_html=True)

try:
    resp = requests.get(f"{API}/documents", timeout=8)
    if resp.status_code == 200:
        data = resp.json()
        docs = data.get("documents", [])

        if not docs:
            st.markdown("""
<div style="background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:var(--radius-xl);
     padding:3rem;text-align:center;margin:1rem 0">
  <div style="font-size:2.5rem;margin-bottom:1rem">📂</div>
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:600;
       color:var(--text-secondary);margin-bottom:0.375rem">No documents indexed yet</div>
  <div style="font-size:0.875rem;color:var(--text-muted)">Upload a PDF, DOCX, or XLSX file above to populate your knowledge base.</div>
</div>
""", unsafe_allow_html=True)
        else:
            # Stats bar
            total_chunks = sum(d.get("chunk_count", 0) for d in docs)
            st.markdown(f"""
<div style="display:flex;gap:2rem;margin-bottom:1.25rem;padding:0.875rem 1.25rem;
     background:var(--bg-elevated);border:1px solid var(--border-subtle);border-radius:var(--radius-lg)">
  <div><span style="font-family:'Space Grotesk',sans-serif;font-size:1.25rem;font-weight:700;
       color:var(--text-primary)">{data['total']}</span>
       <span style="font-size:0.8rem;color:var(--text-muted);margin-left:0.375rem">documents</span></div>
  <div><span style="font-family:'Space Grotesk',sans-serif;font-size:1.25rem;font-weight:700;
       color:var(--indigo-400)">{total_chunks:,}</span>
       <span style="font-size:0.8rem;color:var(--text-muted);margin-left:0.375rem">total chunks</span></div>
  <div style="margin-left:auto"><span class="rea-badge rea-badge-emerald">✓ Vector Store Active</span></div>
</div>
""", unsafe_allow_html=True)

            for doc in docs:
                col_doc, col_del = st.columns([11, 1])
                with col_doc:
                    st.markdown(doc_row(
                        filename=doc["filename"],
                        file_type=doc.get("file_type", "file"),
                        chunks=doc.get("chunk_count", 0),
                        pages=doc.get("page_count", 0),
                    ), unsafe_allow_html=True)
                with col_del:
                    st.markdown("<div style='padding-top:0.5rem'>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{doc['doc_id']}", help="Delete document"):
                        del_resp = requests.delete(f"{API}/documents/{doc['doc_id']}", timeout=15)
                        if del_resp.status_code == 200:
                            st.rerun()
                        else:
                            st.error("Delete failed")
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Could not fetch document list from the API.")

except requests.ConnectionError:
    st.markdown("""
<div style="background:var(--amber-glow);border:1px solid rgba(245,158,11,0.25);border-radius:var(--radius-lg);
     padding:1.25rem 1.5rem;margin-top:1rem">
  <div style="font-weight:600;color:var(--amber-500);margin-bottom:0.25rem">⚠ Backend Not Reachable</div>
  <div style="font-size:0.875rem;color:var(--text-muted)">
    Start the backend first:<br>
    <code style="background:var(--bg-base);padding:2px 8px;border-radius:4px;font-size:0.8rem">
    uvicorn backend.main:app --reload --port 8000
    </code>
  </div>
</div>
""", unsafe_allow_html=True)
