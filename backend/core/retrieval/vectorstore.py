"""
backend/core/retrieval/vectorstore.py
──────────────────────────────────────
ChromaDB wrapper — persistent local vector database.
Handles: upsert, query, delete, list, stats.

ChromaDB persists to disk automatically.
No server needed — embedded mode.
"""
from __future__ import annotations
from functools import lru_cache
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import get_settings
from backend.utils.logger import logger

settings = get_settings()


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.PersistentClient:
    """Singleton ChromaDB persistent client."""
    client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    logger.info(f"ChromaDB ready at {settings.chroma_persist_dir}")
    return client


def get_collection():
    """Get or create the main collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},   # Cosine similarity
    )


# ── Write ─────────────────────────────────────────────────────────────────────
def upsert_chunks(chunks: list[dict[str, Any]], embeddings: list[list[float]]) -> int:
    """
    Upsert chunk embeddings into ChromaDB.

    Args:
        chunks: List of chunk dicts from chunker
        embeddings: Parallel list of embedding vectors

    Returns:
        Number of chunks upserted
    """
    if not chunks:
        return 0

    collection = get_collection()
    ids = [c["chunk_id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            k: str(v) if not isinstance(v, (str, int, float, bool)) else v
            for k, v in c["metadata"].items()
        }
        for c in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    logger.info(f"Upserted {len(chunks)} chunks into ChromaDB")
    return len(chunks)


def delete_document(doc_id: str) -> int:
    """Delete all chunks belonging to a document."""
    collection = get_collection()
    results = collection.get(where={"doc_id": doc_id})
    if not results["ids"]:
        return 0
    collection.delete(ids=results["ids"])
    count = len(results["ids"])
    logger.info(f"Deleted {count} chunks for doc_id={doc_id}")
    return count


# ── Read ──────────────────────────────────────────────────────────────────────
def query_chunks(
    query_embedding: list[float],
    top_k: int = 20,
    where: dict | None = None,
) -> list[dict[str, Any]]:
    """
    ANN query ChromaDB.

    Returns list of result dicts with text, metadata, distance.
    """
    collection = get_collection()

    kwargs: dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": min(top_k, max(collection.count(), 1)),
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)

    output = []
    if results["ids"] and results["ids"][0]:
        for doc_id, doc, meta, dist in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append({
                "chunk_id": doc_id,
                "text": doc,
                "metadata": meta,
                "score": float(1 - dist),   # Chroma cosine returns distance; convert to similarity
            })
    return output


def list_documents() -> list[dict[str, Any]]:
    """Return unique documents from chunk metadata."""
    collection = get_collection()
    if collection.count() == 0:
        return []

    all_items = collection.get(include=["metadatas"])
    seen_docs: dict[str, dict] = {}
    for meta in all_items["metadatas"]:
        doc_id = meta.get("doc_id", "")
        if doc_id and doc_id not in seen_docs:
            seen_docs[doc_id] = meta

    return list(seen_docs.values())


def get_doc_chunk_count(doc_id: str) -> int:
    collection = get_collection()
    results = collection.get(where={"doc_id": doc_id})
    return len(results["ids"])


def collection_stats() -> dict[str, Any]:
    collection = get_collection()
    return {"total_chunks": collection.count()}
