"""
backend/core/tools/doc_retriever.py
─────────────────────────────────────
Internal document retrieval tool — a thin wrapper around the
retrieval pipeline formatted as a LangChain-style tool dict.

Used by the ReAct agent loop in agent.py when it calls
retrieve_internal(query).
"""
from __future__ import annotations
from typing import Any

from backend.core.retrieval.retriever import retrieve
from backend.config import get_settings
from backend.utils.logger import logger

settings = get_settings()


def retrieve_internal(
    query: str,
    top_k: int | None = None,
    doc_id_filter: str | None = None,
) -> list[dict[str, Any]]:
    """
    Tool: retrieve relevant chunks from the internal vector store.

    This is the primary tool the ReAct agent calls when it needs
    to ground its answer in internal company documents.

    Args:
        query:          Natural language query to retrieve for
        top_k:          Override number of chunks to return
        doc_id_filter:  Restrict retrieval to a single document

    Returns:
        List of SourceChunk-compatible dicts
    """
    k = top_k or settings.reranker_top_k
    logger.debug(f"[TOOL] retrieve_internal | query='{query[:60]}...' | top_k={k}")

    results = retrieve(
        query=query,
        top_k_rerank=k,
        doc_id_filter=doc_id_filter,
    )

    logger.debug(f"[TOOL] retrieve_internal → {len(results)} chunks returned")
    return results


# ── Tool descriptor (for agent introspection / future LangChain integration) ─
TOOL_DESCRIPTOR = {
    "name": "retrieve_internal",
    "description": (
        "Search the internal document knowledge base using semantic similarity. "
        "Use this to find relevant passages from uploaded PDFs, DOCX files, "
        "and spreadsheets. Returns ranked, cited text chunks."
    ),
    "parameters": {
        "query": {
            "type": "string",
            "description": "Natural language search query",
            "required": True,
        },
        "top_k": {
            "type": "integer",
            "description": "Max number of chunks to return (default: 5)",
            "required": False,
        },
    },
    "callable": retrieve_internal,
}
