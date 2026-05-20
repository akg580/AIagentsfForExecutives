"""
backend/core/ingestion/embedder.py
Singleton wrapper around embedding model.
Primary: sentence-transformers model.
Fallback: deterministic local hash embedder (offline-safe).
"""

from __future__ import annotations

import hashlib
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import numpy as np

from backend.config import get_settings
from backend.utils.logger import logger

settings = get_settings()


class LocalHashEmbeddingModel:
    """
    Offline-safe deterministic embedding fallback.

    Produces 384-d vectors compatible with Chroma collection dimension.
    """

    def __init__(self, dim: int = 384):
        self.dim = dim

    def get_sentence_embedding_dimension(self) -> int:
        return self.dim

    def encode(
        self,
        texts: Iterable[str],
        batch_size: int = 32,
        show_progress_bar: bool = False,
        normalize_embeddings: bool = True,
        convert_to_numpy: bool = True,
    ):
        _ = (batch_size, show_progress_bar)
        vectors: list[np.ndarray] = []
        for text in texts:
            vectors.append(self._embed_one(text, normalize_embeddings=normalize_embeddings))

        if vectors:
            arr = np.vstack(vectors).astype(np.float32)
        else:
            arr = np.zeros((0, self.dim), dtype=np.float32)

        return arr if convert_to_numpy else arr.tolist()

    def _embed_one(self, text: str, normalize_embeddings: bool) -> np.ndarray:
        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = re.findall(r"\w+", (text or "").lower())
        if not tokens:
            tokens = [""]

        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=16).digest()
            idx_a = int.from_bytes(digest[0:4], "little") % self.dim
            idx_b = int.from_bytes(digest[4:8], "little") % self.dim
            sign_a = 1.0 if (digest[8] & 1) == 0 else -1.0
            sign_b = 1.0 if (digest[9] & 1) == 0 else -1.0
            vec[idx_a] += sign_a
            vec[idx_b] += 0.5 * sign_b

        if normalize_embeddings:
            norm = float(np.linalg.norm(vec))
            if norm > 0:
                vec /= norm
        return vec


def _candidate_model_names(model_name: str) -> list[str]:
    names = [model_name]
    if "/" not in model_name:
        names.append(f"sentence-transformers/{model_name}")
    return names


def _has_local_model_cache(model_name: str) -> bool:
    model_path = Path(model_name)
    if model_path.exists():
        return True

    hf_home = Path(os.getenv("HF_HOME", str(Path.home() / ".cache" / "huggingface")))
    hub_root = hf_home / "hub"

    for name in _candidate_model_names(model_name):
        cache_dir = hub_root / f"models--{name.replace('/', '--')}"
        snapshots = cache_dir / "snapshots"
        if snapshots.exists():
            try:
                if any(snapshots.iterdir()):
                    return True
            except OSError:
                continue
    return False


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load model once and cache in memory."""
    logger.info(f"Loading embedding model: {settings.embedding_model}")

    if not _has_local_model_cache(settings.embedding_model):
        logger.warning(
            "No local embedding model cache found; using offline fallback embedder."
        )
        model = LocalHashEmbeddingModel(dim=384)
        logger.info(f"Fallback embedder ready. Dim={model.get_sentence_embedding_dimension()}")
        return model

    from sentence_transformers import SentenceTransformer
    try:
        model = SentenceTransformer(
            settings.embedding_model,
            device=settings.embedding_device,
            local_files_only=True,
        )
        logger.info(f"Embedding model ready. Dim={model.get_sentence_embedding_dimension()}")
        return model
    except Exception as exc:
        logger.warning(
            "Embedding model could not be loaded (likely offline/no local cache). "
            "Falling back to local hash embeddings. "
            f"Reason: {exc}"
        )
        model = LocalHashEmbeddingModel(dim=384)
        logger.info(f"Fallback embedder ready. Dim={model.get_sentence_embedding_dimension()}")
        return model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of strings.

    Returns list of float vectors (one per text).
    Uses batching internally for efficiency.
    """
    if not texts:
        return []

    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([query])[0]
