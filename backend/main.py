"""
backend/main.py
───────────────
FastAPI application factory.
Registers all routers, CORS middleware, startup events, and error handlers.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.utils.logger import logger
from backend.api.routes import documents, query, reports, health

settings = get_settings()


# ── Lifespan (startup / shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("RAG Executive Analyst API starting up...")
    logger.info(f"  LLM       : {settings.groq_model}")
    logger.info(f"  Embeddings: {settings.embedding_model}")
    logger.info(f"  VectorDB  : ChromaDB @ {settings.chroma_persist_dir}")
    logger.info(f"  Env       : {settings.app_env}")
    yield
    logger.info("RAG Executive Analyst API shutting down.")


# ── App factory ───────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG Executive Analyst API",
        description=(
            "AI-powered business intelligence platform. "
            "Upload internal documents, query them in natural language, "
            "and generate structured, cited executive reports."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url, "http://localhost:8501"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global error handler ─────────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception on {request.url}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)},
        )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
    app.include_router(query.router, prefix="/api/v1", tags=["Query"])
    app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

    return app


app = create_app()


# ── Dev runner ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_env == "development",
        log_level="info",
    )
