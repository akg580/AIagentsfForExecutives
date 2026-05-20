"""
backend/api/routes/query.py
────────────────────────────
POST /api/v1/query — Natural language question → cited answer
"""
import time
from fastapi import APIRouter, HTTPException

from backend.core.generation.agent import answer_query
from backend.models.schemas import QueryRequest, QueryResponse, SourceChunk
from backend.utils.logger import logger

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Ask a natural language question.
    Returns a cited answer grounded in your indexed documents (+ optional web).
    """
    try:
        result = answer_query(
            query=request.query,
            search_mode=request.search_mode,
            top_k=request.top_k,
            include_trace=request.include_trace,
        )
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    sources = [
        SourceChunk(
            doc_id=s.get("doc_id", ""),
            filename=s.get("filename", ""),
            page=s.get("page", 1),
            content=s.get("content", "")[:500],  # Truncate for response size
            score=s.get("score", 0.0),
            source_type=s.get("source_type", "internal"),
            url=s.get("url"),
        )
        for s in result["sources"]
    ]

    return QueryResponse(
        answer=result["answer"],
        sources=sources,
        search_mode=result["search_mode"],
        latency_ms=result["latency_ms"],
        trace=result.get("trace"),
    )
