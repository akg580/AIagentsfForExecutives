"""
backend/config.py
─────────────────
Centralised settings loaded from .env via pydantic-settings.
All configuration lives here — never scattered across modules.
"""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Groq ─────────────────────────────────────────────────────────────────
    groq_api_key: str = "gsk_placeholder"
    groq_model: str = "llama-3.3-70b-versatile"
    groq_max_tokens: int = 4096
    groq_temperature: float = 0.1

    # ── Tavily ───────────────────────────────────────────────────────────────
    tavily_api_key: str = "tvly-placeholder"

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    chroma_persist_dir: str = "./data/chroma_db"
    chroma_collection_name: str = "rag_executive_analyst"

    # ── Embeddings ───────────────────────────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: str = "cpu"

    # ── Reranker ─────────────────────────────────────────────────────────────
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_top_k: int = 5
    retrieval_top_k: int = 20

    # ── Chunking ─────────────────────────────────────────────────────────────
    chunk_size: int = 500
    chunk_overlap: int = 80

    # ── App ───────────────────────────────────────────────────────────────────
    app_env: str = "development"
    app_secret_key: str = "change_me"
    upload_dir: str = "./data/uploads"
    reports_dir: str = "./data/reports"
    max_upload_size_mb: int = 50

    # ── API ───────────────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:8501"

    def ensure_dirs(self) -> None:
        """Create required directories on startup."""
        for d in [self.upload_dir, self.reports_dir, self.chroma_persist_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance — import this everywhere."""
    s = Settings()
    s.ensure_dirs()
    return s
