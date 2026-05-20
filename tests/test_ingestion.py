"""
tests/test_ingestion.py
────────────────────────
Unit tests for the ingestion pipeline.
Run with: pytest tests/ -v
"""
import pytest
from pathlib import Path
import tempfile

from backend.core.ingestion.chunker import chunk_pages, _recursive_split
from backend.core.ingestion.embedder import embed_texts, embed_query


# ── Chunker tests ─────────────────────────────────────────────────────────────
class TestChunker:
    def test_basic_chunking(self):
        pages = [{"text": "Hello world. " * 50, "page": 1, "metadata": {"filename": "test.pdf", "source_type": "internal", "file_type": "pdf", "page": 1, "total_pages": 1}}]
        chunks = chunk_pages(pages, doc_id="test-doc-001", chunk_size=200, chunk_overlap=40)
        assert len(chunks) > 1
        assert all("chunk_id" in c for c in chunks)
        assert all("text" in c for c in chunks)
        assert all(len(c["text"]) > 0 for c in chunks)

    def test_chunk_has_metadata(self):
        pages = [{"text": "Sample text for testing. " * 20, "page": 1, "metadata": {"filename": "sample.pdf", "source_type": "internal", "file_type": "pdf", "page": 1, "total_pages": 1}}]
        chunks = chunk_pages(pages, doc_id="meta-test-001")
        assert all("doc_id" in c["metadata"] for c in chunks)
        assert all(c["metadata"]["doc_id"] == "meta-test-001" for c in chunks)

    def test_short_text_single_chunk(self):
        pages = [{"text": "Short text.", "page": 1, "metadata": {"filename": "short.txt", "source_type": "internal", "file_type": "txt", "page": 1, "total_pages": 1}}]
        chunks = chunk_pages(pages, doc_id="short-001")
        assert len(chunks) == 1

    def test_empty_text_skipped(self):
        pages = [{"text": "", "page": 1, "metadata": {"filename": "empty.txt", "source_type": "internal", "file_type": "txt", "page": 1, "total_pages": 1}}]
        chunks = chunk_pages(pages, doc_id="empty-001")
        assert len(chunks) == 0

    def test_recursive_split(self):
        text = "Para one.\n\nPara two.\n\nPara three."
        chunks = _recursive_split(text, chunk_size=15, overlap=0)
        assert len(chunks) > 0
        assert all(len(c) > 0 for c in chunks)


# ── Embedder tests ────────────────────────────────────────────────────────────
class TestEmbedder:
    def test_embed_single(self):
        vec = embed_query("What is the revenue for Q3?")
        assert isinstance(vec, list)
        assert len(vec) == 384   # all-MiniLM-L6-v2 dimension

    def test_embed_batch(self):
        texts = ["First sentence.", "Second sentence.", "Third sentence."]
        vecs = embed_texts(texts)
        assert len(vecs) == 3
        assert all(len(v) == 384 for v in vecs)

    def test_embed_normalised(self):
        import math
        vec = embed_query("Test normalisation")
        norm = math.sqrt(sum(x ** 2 for x in vec))
        assert abs(norm - 1.0) < 0.01   # Should be L2-normalised

    def test_embed_empty_list(self):
        result = embed_texts([])
        assert result == []
