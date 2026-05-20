"""
backend/core/ingestion/chunker.py
──────────────────────────────────
Recursive character text splitter.
Splits on paragraph → newline → sentence → word boundaries.
Adds per-chunk metadata (doc_id, chunk_index, page, etc.).
"""
from __future__ import annotations
import re
import uuid
from typing import Any

from backend.config import get_settings
from backend.utils.logger import logger

settings = get_settings()


def chunk_pages(
    pages: list[dict[str, Any]],
    doc_id: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[dict[str, Any]]:
    """
    Takes loader output (page dicts) and returns flat list of chunk dicts.

    Each chunk dict:
        chunk_id   : unique UUID
        doc_id     : parent document id
        text       : chunk text
        page       : source page number
        chunk_index: index within document
        metadata   : dict with filename, file_type, source_type, etc.
    """
    cs = chunk_size or settings.chunk_size
    co = chunk_overlap or settings.chunk_overlap

    all_chunks = []
    global_idx = 0

    for page in pages:
        raw_text = page["text"]
        page_meta = page["metadata"]

        raw_chunks = _recursive_split(raw_text, cs, co)

        for local_idx, chunk_text in enumerate(raw_chunks):
            if not chunk_text.strip():
                continue
            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "doc_id": doc_id,
                "text": chunk_text.strip(),
                "page": page_meta.get("page", 1),
                "chunk_index": global_idx,
                "metadata": {
                    **page_meta,
                    "doc_id": doc_id,
                    "chunk_index": global_idx,
                    "local_chunk_index": local_idx,
                }
            })
            global_idx += 1

    logger.info(f"  → Chunked into {len(all_chunks)} chunks "
                f"(size={cs}, overlap={co}) for doc_id={doc_id}")
    return all_chunks


# ── Recursive split ───────────────────────────────────────────────────────────
_SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]


def _recursive_split(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Recursively split text using decreasing granularity separators."""
    return _split_with_sep(text, chunk_size, overlap, _SEPARATORS)


def _split_with_sep(
    text: str, chunk_size: int, overlap: int, separators: list[str]
) -> list[str]:
    if not text.strip():
        return []

    # If text fits in a chunk, return it
    if len(text) <= chunk_size:
        return [text]

    # Try each separator
    for sep in separators:
        if sep == "" or sep in text:
            parts = text.split(sep) if sep else list(text)
            return _merge_parts(parts, sep, chunk_size, overlap)

    return [text[:chunk_size]]


def _merge_parts(
    parts: list[str], separator: str, chunk_size: int, overlap: int
) -> list[str]:
    """Merge split parts into chunks respecting size + overlap constraints."""
    chunks = []
    current: list[str] = []
    current_len = 0

    for part in parts:
        part_len = len(part) + len(separator)

        if current_len + part_len > chunk_size and current:
            # Flush current chunk
            chunks.append(separator.join(current))

            # Keep overlap: remove from front until overlap constraint is met
            while current and current_len > overlap:
                removed = current.pop(0)
                current_len -= len(removed) + len(separator)

        current.append(part)
        current_len += part_len

    if current:
        chunks.append(separator.join(current))

    return [c for c in chunks if c.strip()]
