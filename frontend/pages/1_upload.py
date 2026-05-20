"""
frontend/pages/1_upload.py
Upload and manage documents page.
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

st.set_page_config(page_title="Upload Documents", layout="wide")
apply_enterprise_theme()
render_sidebar()

st.title("Upload Documents")
st.caption("Index PDF, DOCX, XLSX, or TXT files into the vector store.")

st.markdown("### Upload New Document")

uploaded = st.file_uploader(
    "Choose a file",
    type=["pdf", "docx", "doc", "xlsx", "xls", "txt", "md"],
    help="Max 50MB. Supported: PDF, Word, Excel, Text, Markdown",
)

if uploaded:
    col1, col2 = st.columns([3, 1])
    col1.info(f"**{uploaded.name}** | {uploaded.size / 1024:.1f} KB")

    if col2.button("Upload and Index", type="primary", use_container_width=True):
        with st.spinner(f"Ingesting '{uploaded.name}'..."):
            try:
                response = requests.post(
                    f"{API}/documents/upload",
                    files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)},
                    timeout=120,
                )
                if response.status_code == 201:
                    data = response.json()
                    st.success(
                        f"**{uploaded.name}** indexed successfully.\n\n"
                        f"Chunks created: **{data['chunk_count']}**\n\n"
                        f"Document ID: `{data['doc_id']}`"
                    )
                else:
                    st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
            except requests.Timeout:
                st.error("Upload timed out. Please retry with a smaller file or try again shortly.")
            except requests.ConnectionError:
                st.error("Cannot connect to backend. Run: `uvicorn backend.main:app --reload --port 8000`")

st.markdown("---")
st.markdown("### Indexed Documents")

try:
    resp = requests.get(f"{API}/documents", timeout=20)
    if resp.status_code == 200:
        data = resp.json()
        docs = data.get("documents", [])

        if not docs:
            st.info("No documents indexed yet. Upload one above to get started.")
        else:
            st.caption(f"Total documents: **{data['total']}**")

            for doc in docs:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                    col1.markdown(f"**{doc['filename']}**")
                    col2.caption(doc["file_type"].upper())
                    col3.caption(f"{doc['chunk_count']} chunks")
                    col4.caption(f"{doc['page_count']} pages")

                    if col5.button("Delete", key=f"del_{doc['doc_id']}", use_container_width=True):
                        try:
                            del_resp = requests.delete(f"{API}/documents/{doc['doc_id']}", timeout=20)
                            if del_resp.status_code == 200:
                                st.success(f"Deleted {doc['filename']}")
                                st.rerun()
                            else:
                                st.error("Delete failed")
                        except requests.Timeout:
                            st.error("Delete request timed out. Please retry.")
                        except requests.ConnectionError:
                            st.error("Backend offline. Run: `uvicorn backend.main:app --reload --port 8000`")

                    st.divider()
    else:
        st.warning("Could not load document list.")

except requests.Timeout:
    st.warning("Document list request timed out. Backend may be busy; refresh in a few seconds.")
except requests.ConnectionError:
    st.warning("Backend offline. Start it with: `uvicorn backend.main:app --reload --port 8000`")
