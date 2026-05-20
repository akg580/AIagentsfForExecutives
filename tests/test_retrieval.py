"""
tests/test_retrieval.py
────────────────────────
Unit tests for the retrieval pipeline.
Mocks ChromaDB and embedding model to avoid needing infra.

Run with: pytest tests/test_retrieval.py -v
"""
import pytest
from unittest.mock import patch, MagicMock

from backend.core.retrieval.reranker import rerank


# ── Reranker tests ────────────────────────────────────────────────────────────
class TestReranker:
    def test_rerank_empty_returns_empty(self):
        result = rerank("test query", [])
        assert result == []

    def test_rerank_orders_by_score(self):
        chunks = [
            {"text": "Irrelevant text about weather.", "score": 0.9},
            {"text": "Q3 revenue increased by 15% to $5.2M.", "score": 0.5},
        ]

        mock_scores = [0.1, 0.95]  # Second chunk should rank first after reranking
        mock_model = MagicMock()
        mock_model.predict.return_value = mock_scores

        with patch("backend.core.retrieval.reranker.get_reranker", return_value=mock_model):
            result = rerank("What was Q3 revenue?", chunks, top_k=2)

        # Second chunk (revenue) should now be first
        assert result[0]["text"] == "Q3 revenue increased by 15% to $5.2M."
        assert result[0]["score"] == 0.95

    def test_rerank_respects_top_k(self):
        chunks = [{"text": f"Chunk {i}", "score": float(i) / 10} for i in range(10)]
        mock_model = MagicMock()
        mock_model.predict.return_value = [float(i) / 10 for i in range(10)]

        with patch("backend.core.retrieval.reranker.get_reranker", return_value=mock_model):
            result = rerank("test", chunks, top_k=3)

        assert len(result) == 3

    def test_rerank_adds_original_score(self):
        chunks = [{"text": "Some text", "score": 0.7}]
        mock_model = MagicMock()
        mock_model.predict.return_value = [0.88]

        with patch("backend.core.retrieval.reranker.get_reranker", return_value=mock_model):
            result = rerank("test query", chunks, top_k=1)

        assert "original_score" in result[0]
        assert result[0]["original_score"] == 0.7
        assert result[0]["rerank_score"] == 0.88


# ── Retriever integration tests ───────────────────────────────────────────────
class TestRetriever:
    def test_retriever_returns_empty_on_no_docs(self):
        with patch("backend.core.retrieval.retriever.embed_query", return_value=[0.0] * 384), \
             patch("backend.core.retrieval.retriever.query_chunks", return_value=[]):
            from backend.core.retrieval.retriever import retrieve
            result = retrieve("What is revenue?")
        assert result == []

    def test_retriever_formats_output_correctly(self):
        mock_chunk = {
            "chunk_id": "test-chunk-001",
            "text": "Revenue increased to $5M in Q3.",
            "score": 0.85,
            "rerank_score": 0.92,
            "original_score": 0.85,
            "metadata": {
                "doc_id": "doc-001",
                "filename": "board_report.pdf",
                "page": "4",
                "source_type": "internal",
                "file_type": "pdf",
            },
        }

        with patch("backend.core.retrieval.retriever.embed_query", return_value=[0.1] * 384), \
             patch("backend.core.retrieval.retriever.query_chunks", return_value=[mock_chunk]), \
             patch("backend.core.retrieval.retriever.rerank", return_value=[mock_chunk]):
            from backend.core.retrieval.retriever import retrieve
            result = retrieve("What was Q3 revenue?")

        assert len(result) == 1
        r = result[0]
        assert r["doc_id"] == "doc-001"
        assert r["filename"] == "board_report.pdf"
        assert r["page"] == 4
        assert r["source_type"] == "internal"
        assert r["url"] is None
        assert "content" in r
