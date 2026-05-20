"""
backend/core/retrieval/retriever.py
─────────────────────────────────────
Orchestrates the full retrieval pipeline:
  1. Embed query
  2. ANN search in ChromaDB (top-20)
  3. Cross-encoder rerank (top-5)
  4. Return SourceChunk-compatible dicts
"""
from __future__ import annotations
from typing import Any

from backend.core.ingestion.embedder import embed_query
from backend.core.retrieval.vectorstore import query_chunks
from backend.core.retrieval.reranker import rerank
from backend.config import get_settings
from backend.utils.logger import logger

settings = get_settings()


def retrieve(
    query: str,
    top_k_retrieve: int | None = None,
    top_k_rerank: int | None = None,
    doc_id_filter: str | None = None,
) -> list[dict[str, Any]]:
    """
    Full retrieval pipeline: embed → ANN → rerank.

    Returns list of dicts compatible with SourceChunk schema.
    """
    k_retrieve = top_k_retrieve or settings.retrieval_top_k
    k_rerank = top_k_rerank or settings.reranker_top_k

    # Step 1: Embed
    logger.debug(f"Retrieving for query: '{query[:80]}...'")
    query_vec = embed_query(query)

    # Step 2: ANN search
    where_filter = {"doc_id": doc_id_filter} if doc_id_filter else None
    raw_results = query_chunks(query_vec, top_k=k_retrieve, where=where_filter)

    if not raw_results:
        logger.warning("No chunks found in vector store for this query")
        return []

    # Step 3: Rerank
    reranked = rerank(query, raw_results, top_k=k_rerank)

    # Step 4: Format output
    output = []
    for chunk in reranked:
        meta = chunk.get("metadata", {})
        output.append({
            "chunk_id": chunk.get("chunk_id", ""),
            "doc_id": meta.get("doc_id", ""),
            "filename": meta.get("filename", "unknown"),
            "page": int(meta.get("page", 1)),
            "content": chunk["text"],
            "score": round(chunk["score"], 4),
            "source_type": "internal",
            "url": None,
        })

    logger.info(
        f"Retrieval complete: {len(raw_results)} → reranked → {len(output)} chunks "
        f"(scores: {[round(c['score'],3) for c in output]})"
    )
    return output
