"""
backend/api/routes/reports.py
──────────────────────────────
POST   /api/v1/reports/generate        — Generate full executive report
GET    /api/v1/reports/{id}/export     — Download report as DOCX
"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from backend.config import get_settings
from backend.core.generation.agent import generate_report
from backend.core.export.docx_exporter import export_report_to_docx
from backend.models.schemas import (
    ReportRequest, ReportResponse, ReportSection_Out,
    SourceChunk, ExportFormat
)
from backend.utils.logger import logger

router = APIRouter()
settings = get_settings()

# In-memory report cache (use Redis in production)
_report_cache: dict[str, dict] = {}


@router.post("/generate", response_model=ReportResponse)
async def generate_report_endpoint(request: ReportRequest):
    """
    Generate a structured, multi-section executive report.

    The agent will:
    1. Retrieve relevant chunks from indexed documents
    2. Optionally search the web for market context
    3. Generate each section with inline [SOURCE N] citations
    4. Return the full structured report
    """
    sections = [s.value for s in request.sections]

    try:
        report = generate_report(
            title=request.title,
            query=request.query,
            sections=sections,
            search_mode=request.search_mode,
            include_trace=request.include_trace,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

    # Cache for export
    _report_cache[report["report_id"]] = report

    # Also save JSON to disk for persistence
    report_path = Path(settings.reports_dir) / f"{report['report_id']}.json"
    try:
        report_path.write_text(
            json.dumps({
                **report,
                "generated_at": report["generated_at"].isoformat(),
            }, default=str),
            encoding="utf-8"
        )
    except Exception as e:
        logger.warning(f"Could not save report JSON: {e}")

    # Build response
    sections_out = [
        ReportSection_Out(
            section=s["section"],
            content=s["content"],
            sources=[
                SourceChunk(
                    doc_id=src.get("doc_id", ""),
                    filename=src.get("filename", ""),
                    page=src.get("page", 1),
                    content=src.get("content", "")[:400],
                    score=src.get("score", 0.0),
                    source_type=src.get("source_type", "internal"),
                    url=src.get("url"),
                )
                for src in s.get("sources", [])[:5]   # Limit per-section source list
            ],
        )
        for s in report["sections"]
    ]

    all_sources = [
        SourceChunk(
            doc_id=s.get("doc_id", ""),
            filename=s.get("filename", ""),
            page=s.get("page", 1),
            content=s.get("content", "")[:400],
            score=s.get("score", 0.0),
            source_type=s.get("source_type", "internal"),
            url=s.get("url"),
        )
        for s in report["all_sources"]
    ]

    return ReportResponse(
        report_id=report["report_id"],
        title=report["title"],
        query=report["query"],
        sections=sections_out,
        all_sources=all_sources,
        generated_at=report["generated_at"],
        latency_ms=report["latency_ms"],
        trace=report.get("trace"),
    )


@router.get("/{report_id}/export")
async def export_report(
    report_id: str,
    format: ExportFormat = Query(ExportFormat.docx),
):
    """
    Download a previously generated report as DOCX or Markdown.
    """
    # Check memory cache first
    report = _report_cache.get(report_id)

    # Fall back to disk
    if not report:
        report_path = Path(settings.reports_dir) / f"{report_id}.json"
        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_id}' not found. Generate it first.",
            )
        report = json.loads(report_path.read_text())

    if format == ExportFormat.docx:
        docx_bytes = export_report_to_docx(report)
        safe_title = "".join(c if c.isalnum() or c in "- _" else "_" for c in report.get("title", "report"))
        filename = f"{safe_title[:50]}.docx"

        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    elif format == ExportFormat.markdown:
        lines = [f"# {report.get('title', 'Report')}\n"]
        lines.append(f"**Query:** {report.get('query', '')}\n")
        lines.append(f"**Generated:** {report.get('generated_at', '')}\n\n---\n")

        for section in report.get("sections", []):
            lines.append(f"## {section.get('section', 'Section')}\n")
            lines.append(section.get("content", "") + "\n\n")

        lines.append("## Sources\n")
        for i, src in enumerate(report.get("all_sources", []), 1):
            if src.get("source_type") == "web":
                lines.append(f"{i}. [{src.get('filename', 'Web')}]({src.get('url', '')})\n")
            else:
                lines.append(f"{i}. {src.get('filename', '?')} — Page {src.get('page', '?')}\n")

        md_content = "\n".join(lines)
        return Response(
            content=md_content.encode("utf-8"),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="report.md"'},
        )
