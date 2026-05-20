"""
backend/models/schemas.py
─────────────────────────
All Pydantic request/response models in one place.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────────────────
class SearchMode(str, Enum):
    internal = "internal"           # Only indexed documents
    web = "web"                     # Only web search
    hybrid = "hybrid"               # Internal + web (recommended)


class ReportSection(str, Enum):
    executive_summary = "executive_summary"
    key_findings = "key_findings"
    data_table = "data_table"
    market_context = "market_context"
    risk_factors = "risk_factors"
    recommendations = "recommendations"


class ExportFormat(str, Enum):
    docx = "docx"
    markdown = "markdown"


# ── Document schemas ─────────────────────────────────────────────────────────
class DocumentMetadata(BaseModel):
    doc_id: str
    filename: str
    file_type: str
    page_count: int
    chunk_count: int
    uploaded_at: datetime
    size_bytes: int


class DocumentListResponse(BaseModel):
    documents: list[DocumentMetadata]
    total: int


class IngestResponse(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int
    message: str


class DeleteResponse(BaseModel):
    doc_id: str
    message: str


# ── Query schemas ─────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=2000,
                       description="Natural language question or report request")
    search_mode: SearchMode = Field(SearchMode.hybrid,
                                    description="Where to search for evidence")
    top_k: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve")
    include_trace: bool = Field(False, description="Return agent reasoning trace")


class SourceChunk(BaseModel):
    doc_id: str
    filename: str
    page: int
    content: str
    score: float
    source_type: str    # "internal" or "web"
    url: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    search_mode: SearchMode
    latency_ms: float
    trace: Optional[list[dict]] = None


# ── Report schemas ────────────────────────────────────────────────────────────
class ReportRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    query: str = Field(..., min_length=10, max_length=2000,
                       description="Research question driving the report")
    search_mode: SearchMode = Field(SearchMode.hybrid)
    sections: list[ReportSection] = Field(
        default=[
            ReportSection.executive_summary,
            ReportSection.key_findings,
            ReportSection.market_context,
            ReportSection.risk_factors,
            ReportSection.recommendations,
        ]
    )
    include_trace: bool = False


class ReportSection_Out(BaseModel):
    section: str
    content: str
    sources: list[SourceChunk]


class ReportResponse(BaseModel):
    report_id: str
    title: str
    query: str
    sections: list[ReportSection_Out]
    all_sources: list[SourceChunk]
    generated_at: datetime
    latency_ms: float
    trace: Optional[list[dict]] = None


class ReportListItem(BaseModel):
    report_id: str
    title: str
    query: str
    generated_at: datetime
    section_count: int


# ── Health ────────────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict[str, str]
