"""
tests/test_api.py
──────────────────
Integration tests for the FastAPI routes.
Uses TestClient — no live server needed.

Run with: pytest tests/test_api.py -v
"""
import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.main import app

client = TestClient(app)


# ── Health ────────────────────────────────────────────────────────────────────
class TestHealth:
    def test_health_returns_200(self):
        with patch("backend.api.routes.health.collection_stats", return_value={"total_chunks": 10}), \
             patch("backend.api.routes.health.get_groq_client", return_value=MagicMock()), \
             patch("backend.api.routes.health.get_embedding_model", return_value=MagicMock()):
            resp = client.get("/api/v1/health")
        assert resp.status_code == 200

    def test_health_has_required_fields(self):
        with patch("backend.api.routes.health.collection_stats", return_value={"total_chunks": 0}), \
             patch("backend.api.routes.health.get_groq_client", return_value=MagicMock()), \
             patch("backend.api.routes.health.get_embedding_model", return_value=MagicMock()):
            resp = client.get("/api/v1/health")
        data = resp.json()
        assert "status" in data
        assert "version" in data
        assert "services" in data


# ── Documents ─────────────────────────────────────────────────────────────────
class TestDocuments:
    def test_list_documents_empty(self):
        with patch("backend.api.routes.documents.list_documents", return_value=[]):
            resp = client.get("/api/v1/documents")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["documents"] == []

    def test_upload_unsupported_type_rejected(self):
        fake_file = io.BytesIO(b"fake content")
        resp = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.exe", fake_file, "application/octet-stream")},
        )
        assert resp.status_code == 400
        assert "Unsupported file type" in resp.json()["detail"]

    def test_upload_pdf_success(self):
        """Mock the full ingestion pipeline for a PDF upload."""
        fake_pdf = b"%PDF-1.4 fake pdf content " * 20

        with patch("backend.api.routes.documents.load_document",
                   return_value=[{"text": "Test content", "page": 1,
                                  "metadata": {"filename": "test.pdf", "source_type": "internal",
                                               "file_type": "pdf", "page": 1, "total_pages": 1}}]), \
             patch("backend.api.routes.documents.chunk_pages",
                   return_value=[{"chunk_id": "abc123", "doc_id": "test-id", "text": "Test content",
                                  "page": 1, "chunk_index": 0, "metadata": {"doc_id": "test-id",
                                  "filename": "test.pdf", "source_type": "internal", "file_type": "pdf",
                                  "page": 1, "total_pages": 1, "chunk_index": 0, "local_chunk_index": 0}}]), \
             patch("backend.api.routes.documents.embed_texts", return_value=[[0.1] * 384]), \
             patch("backend.api.routes.documents.upsert_chunks", return_value=1):

            resp = client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.pdf", io.BytesIO(fake_pdf), "application/pdf")},
            )

        assert resp.status_code == 201
        data = resp.json()
        assert data["chunk_count"] == 1
        assert "doc_id" in data
        assert data["filename"] == "test.pdf"


# ── Query ─────────────────────────────────────────────────────────────────────
class TestQuery:
    def test_query_too_short_rejected(self):
        resp = client.post("/api/v1/query", json={"query": "hi"})
        assert resp.status_code == 422   # Pydantic validation

    def test_query_success(self):
        mock_result = {
            "answer": "The Q3 revenue was $5.2M based on [SOURCE 1].",
            "sources": [{
                "chunk_id": "c1", "doc_id": "d1", "filename": "report.pdf",
                "page": 3, "content": "Q3 revenue: $5.2M", "score": 0.91,
                "source_type": "internal", "url": None,
            }],
            "search_mode": "hybrid",
            "latency_ms": 1234.5,
            "trace": None,
        }
        with patch("backend.api.routes.query.answer_query", return_value=mock_result):
            resp = client.post("/api/v1/query", json={
                "query": "What was the Q3 revenue?",
                "search_mode": "hybrid",
                "top_k": 5,
                "include_trace": False,
            })

        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert len(data["sources"]) == 1
        assert data["latency_ms"] == 1234.5


# ── Reports ───────────────────────────────────────────────────────────────────
class TestReports:
    def test_report_missing_title_rejected(self):
        resp = client.post("/api/v1/reports/generate", json={
            "title": "",
            "query": "What are the key findings from Q3?",
        })
        assert resp.status_code == 422

    def test_report_no_documents_raises_422(self):
        with patch("backend.api.routes.reports.generate_report",
                   side_effect=ValueError("No evidence found.")):
            resp = client.post("/api/v1/reports/generate", json={
                "title": "Q3 Analysis",
                "query": "What are the key findings from Q3 board report?",
                "search_mode": "internal",
                "sections": ["executive_summary"],
            })
        assert resp.status_code == 422

    def test_report_export_not_found(self):
        resp = client.get("/api/v1/reports/nonexistent-id/export?format=docx")
        assert resp.status_code == 404
