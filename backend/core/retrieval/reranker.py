"""
backend/core/retrieval/reranker.py
────────────────────────────────────
Cross-encoder reranker using ms-marco-MiniLM-L-6-v2.
Runs locally — zero API cost.

Why rerank?
  Bi-encoder (embedding) retrieval = fast but coarse.
  Cross-encoder reranking = joint scoring of (query, chunk) pairs.
  MRR improvement: +15–25% over bi-encoder alone.
"""
from __future__ import annotations
from functools import lru_cache

from backend.config import get_settings
from backend.utils.logger import logger

settings = get_settings()


@lru_cache(maxsize=1)
def get_reranker():
    """Load cross-encoder model once."""
    from sentence_transformers import CrossEncoder
    logger.info(f"Loading reranker: {settings.reranker_model}")
    model = CrossEncoder(settings.reranker_model, max_length=512)
    logger.info("  → Reranker ready")
    return model


def rerank(
    query: str,
    chunks: list[dict],
    top_k: int | None = None,
) -> list[dict]:
    """
    Re-score retrieved chunks using cross-encoder.

    Args:
        query: Original user query
        chunks: Retrieved chunks from ANN search (each has 'text' key)
        top_k: How many to return after reranking

    Returns:
        Re-ordered chunks with updated 'score' field
    """
    if not chunks:
        return []

    k = top_k or settings.reranker_top_k
    model = get_reranker()

    # Build (query, passage) pairs
    pairs = [(query, c["text"]) for c in chunks]
    scores = model.predict(pairs, show_progress_bar=False).tolist()

    # Attach reranker scores
    for chunk, score in zip(chunks, scores):
        chunk["rerank_score"] = float(score)
        chunk["original_score"] = chunk.get("score", 0.0)
        chunk["score"] = float(score)    # Override with reranker score

    # Sort by reranker score descending
    reranked = sorted(chunks, key=lambda c: c["rerank_score"], reverse=True)
    result = reranked[:k]

    logger.debug(f"Reranked {len(chunks)} → top {len(result)} chunks")
    return result
