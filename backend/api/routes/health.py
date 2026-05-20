"""backend/api/routes/health.py"""
from fastapi import APIRouter
from backend.models.schemas import HealthResponse
from backend.core.retrieval.vectorstore import collection_stats, get_chroma_client

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check — verifies all services are reachable."""
    services = {}

    # ChromaDB check
    try:
        stats = collection_stats()
        services["chromadb"] = f"ok | {stats['total_chunks']} chunks"
    except Exception as e:
        services["chromadb"] = f"error: {e}"

    # Groq check (lightweight)
    try:
        from backend.core.generation.llm import get_groq_client
        get_groq_client()
        services["groq"] = "ok"
    except Exception as e:
        services["groq"] = f"error: {e}"

    # Embeddings check
    try:
        from backend.core.ingestion.embedder import get_embedding_model
        get_embedding_model()
        services["embeddings"] = "ok (local)"
    except Exception as e:
        services["embeddings"] = f"error: {e}"

    all_ok = all("error" not in v for v in services.values())

    return HealthResponse(
        status="healthy" if all_ok else "degraded",
        version="1.0.0",
        services=services,
    )
