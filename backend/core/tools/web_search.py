"""
backend/core/tools/web_search.py
─────────────────────────────────
Tavily web search tool — free tier (1,000 searches/month).
Returns clean text results formatted as SourceChunk-compatible dicts.

Tavily is RAG-optimised: returns text excerpts, not raw HTML.
"""
from __future__ import annotations

from tenacity import retry, stop_after_attempt, wait_exponential

from backend.config import get_settings
from backend.utils.logger import logger

settings = get_settings()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10), reraise=True)
def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web via Tavily API.

    Returns list of dicts compatible with SourceChunk schema:
        doc_id, filename, page, content, score, source_type, url
    """
    from tavily import TavilyClient

    client = TavilyClient(api_key=settings.tavily_api_key)

    logger.info(f"Web search: '{query[:80]}'")

    response = client.search(
        query=query,
        search_depth="advanced",    # Better results than "basic"
        max_results=max_results,
        include_answer=True,        # Tavily's own summarised answer
        include_raw_content=False,
    )

    results = []

    # Add individual result chunks
    for i, r in enumerate(response.get("results", [])):
        content = r.get("content", "").strip()
        url = r.get("url", "")
        title = r.get("title", url)
        score = float(r.get("score", 0.5))

        if not content:
            continue

        results.append({
            "chunk_id": f"web_{i}_{hash(url)}",
            "doc_id": f"web_{hash(url)}",
            "filename": title[:80],
            "page": 1,
            "content": content,
            "score": score,
            "source_type": "web",
            "url": url,
        })

    logger.info(f"  → Web search returned {len(results)} results")
    return results
