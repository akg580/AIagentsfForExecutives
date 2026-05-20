"""
backend/api/routes/documents.py
─────────────────────────────────
POST /api/v1/documents/upload    — Upload + ingest a document
GET  /api/v1/documents           — List all indexed documents
DELETE /api/v1/documents/{doc_id} — Delete a document + its chunks
"""
from __future__ import annotations
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, status

from backend.config import get_settings
from backend.core.ingestion.loader import load_document
from backend.core.ingestion.chunker import chunk_pages
from backend.core.ingestion.embedder import embed_texts
from backend.core.retrieval.vectorstore import (
    upsert_chunks, delete_document, list_documents, get_doc_chunk_count
)
from backend.models.schemas import IngestResponse, DocumentListResponse, DocumentMetadata, DeleteResponse
from backend.utils.logger import logger

router = APIRouter()
settings = get_settings()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt", ".md"}


@router.post("/upload", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document, chunk it, embed it, and store in ChromaDB.
    Supports: PDF, DOCX, XLSX, TXT, MD.
    """
    # ── Validate ──────────────────────────────────────────────────────────────
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.max_upload_size_mb}MB",
        )

    # ── Save to disk ──────────────────────────────────────────────────────────
    doc_id = str(uuid.uuid4())
    save_path = Path(settings.upload_dir) / f"{doc_id}{suffix}"
    save_path.write_bytes(content)
    logger.info(f"Saved upload: {file.filename} → {save_path}")

    # ── Ingest pipeline ───────────────────────────────────────────────────────
    try:
        # 1. Load
        pages = load_document(str(save_path), file.filename or "document")

        # 2. Chunk
        chunks = chunk_pages(pages, doc_id=doc_id)

        if not chunks:
            raise ValueError("No text could be extracted from this document.")

        # 3. Embed
        texts = [c["text"] for c in chunks]
        embeddings = embed_texts(texts)

        # 4. Store in ChromaDB
        upsert_chunks(chunks, embeddings)

    except Exception as e:
        # Clean up saved file on error
        save_path.unlink(missing_ok=True)
        logger.error(f"Ingestion failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    logger.info(f"✓ Ingested {file.filename} | doc_id={doc_id} | chunks={len(chunks)}")

    return IngestResponse(
        doc_id=doc_id,
        filename=file.filename or "document",
        chunk_count=len(chunks),
        message=f"Successfully ingested '{file.filename}' into {len(chunks)} searchable chunks.",
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents_endpoint():
    """List all documents currently indexed in the vector store."""
    doc_metas = list_documents()

    documents = []
    for meta in doc_metas:
        doc_id = meta.get("doc_id", "")
        documents.append(DocumentMetadata(
            doc_id=doc_id,
            filename=meta.get("filename", "unknown"),
            file_type=meta.get("file_type", "unknown"),
            page_count=int(meta.get("total_pages", 0)),
            chunk_count=get_doc_chunk_count(doc_id),
            uploaded_at=datetime.utcnow(),
            size_bytes=0,   # Not stored in ChromaDB metadata
        ))

    return DocumentListResponse(documents=documents, total=len(documents))


@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document_endpoint(doc_id: str):
    """Delete a document and all its chunks from the vector store."""
    deleted_count = delete_document(doc_id)

    if deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Document '{doc_id}' not found in vector store.",
        )

    # Also remove the uploaded file if it exists
    for ext in ALLOWED_EXTENSIONS:
        f = Path(settings.upload_dir) / f"{doc_id}{ext}"
        if f.exists():
            f.unlink()
            break

    return DeleteResponse(
        doc_id=doc_id,
        message=f"Deleted document {doc_id} and {deleted_count} associated chunks.",
    )
