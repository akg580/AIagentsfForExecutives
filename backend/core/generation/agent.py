"""
backend/core/generation/agent.py
──────────────────────────────────
ReAct (Reason + Act) agent loop for report generation.

Loop structure:
  1. THINK  → Decide which tools to call
  2. ACT    → Call retrieve_internal and/or web_search
  3. OBSERVE → Collect evidence
  4. THINK  → Assess sufficiency
  5. GENERATE → Produce each report section with citations

The agent always calls both internal retrieval AND web search
when search_mode == "hybrid" (recommended default).
"""
from __future__ import annotations
import time
import uuid
from datetime import datetime
from typing import Any

from backend.core.retrieval.retriever import retrieve
from backend.core.tools.web_search import web_search
from backend.core.generation.llm import chat_complete, build_context_block
from backend.core.generation.templates import (
    SYSTEM_PROMPT, QUERY_ANSWER_PROMPT,
    get_section_prompt, SECTION_DISPLAY_NAMES
)
from backend.models.schemas import SearchMode
from backend.utils.logger import logger


# ── Simple Q&A (no full report) ───────────────────────────────────────────────
def answer_query(
    query: str,
    search_mode: SearchMode = SearchMode.hybrid,
    top_k: int = 5,
    include_trace: bool = False,
) -> dict[str, Any]:
    """
    Answer a single natural-language question with citations.

    Returns:
        answer, sources, latency_ms, (optional trace)
    """
    t0 = time.time()
    trace = []

    # ── THINK: Plan evidence gathering ──
    trace.append({"step": "THINK", "content": f"Query: {query}\nMode: {search_mode}"})

    all_sources = []

    # ── ACT: Internal retrieval ──
    if search_mode in (SearchMode.internal, SearchMode.hybrid):
        trace.append({"step": "ACT", "content": "Calling retrieve_internal()"})
        internal = retrieve(query, top_k_rerank=top_k)
        all_sources.extend(internal)
        trace.append({"step": "OBSERVE", "content": f"Got {len(internal)} internal chunks"})

    # ── ACT: Web search ──
    if search_mode in (SearchMode.web, SearchMode.hybrid):
        trace.append({"step": "ACT", "content": "Calling web_search()"})
        try:
            web_results = web_search(query, max_results=3)
            all_sources.extend(web_results)
            trace.append({"step": "OBSERVE", "content": f"Got {len(web_results)} web results"})
        except Exception as e:
            logger.warning(f"Web search failed: {e}")
            trace.append({"step": "OBSERVE", "content": f"Web search failed: {e}"})

    # ── THINK: Assess evidence ──
    trace.append({"step": "THINK", "content": f"Total evidence chunks: {len(all_sources)}"})

    # ── GENERATE: LLM answer ──
    context = build_context_block(all_sources)
    prompt = QUERY_ANSWER_PROMPT.format(query=query, context=context)

    answer = chat_complete(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
    )

    trace.append({"step": "ANSWER", "content": answer[:200] + "..."})

    latency_ms = round((time.time() - t0) * 1000, 1)
    logger.info(f"Query answered in {latency_ms}ms | sources={len(all_sources)}")

    return {
        "answer": answer,
        "sources": all_sources,
        "search_mode": search_mode,
        "latency_ms": latency_ms,
        "trace": trace if include_trace else None,
    }


# ── Full Report Generation ────────────────────────────────────────────────────
def generate_report(
    title: str,
    query: str,
    sections: list[str],
    search_mode: SearchMode = SearchMode.hybrid,
    include_trace: bool = False,
) -> dict[str, Any]:
    """
    Generate a structured, multi-section executive report.

    Each section is generated with its own focused LLM call,
    all grounded in the same retrieved evidence pool.

    Returns:
        report_id, title, query, sections (list), all_sources, generated_at, latency_ms, trace
    """
    t0 = time.time()
    report_id = str(uuid.uuid4())
    trace = []

    logger.info(f"Generating report: '{title}' | sections={sections} | mode={search_mode}")

    # ── THINK: Plan ──
    trace.append({
        "step": "THINK",
        "content": (
            f"Report: {title}\n"
            f"Query: {query}\n"
            f"Sections: {sections}\n"
            f"Mode: {search_mode}"
        )
    })

    all_sources: list[dict] = []

    # ── ACT: Gather evidence ──
    if search_mode in (SearchMode.internal, SearchMode.hybrid):
        trace.append({"step": "ACT", "content": "retrieve_internal(query)"})
        internal = retrieve(query, top_k_rerank=settings_top_k())
        all_sources.extend(internal)
        trace.append({"step": "OBSERVE", "content": f"{len(internal)} internal chunks retrieved"})

    if search_mode in (SearchMode.web, SearchMode.hybrid):
        # For market_context sections, do a broader web search
        web_query = f"{query} industry trends market analysis 2025"
        trace.append({"step": "ACT", "content": f"web_search('{web_query[:60]}')"})
        try:
            web = web_search(web_query, max_results=5)
            all_sources.extend(web)
            trace.append({"step": "OBSERVE", "content": f"{len(web)} web results retrieved"})
        except Exception as e:
            logger.warning(f"Web search failed: {e}")
            trace.append({"step": "OBSERVE", "content": f"Web search error: {e}"})

    if not all_sources:
        raise ValueError(
            "No evidence found. Please upload relevant documents before generating a report."
        )

    # ── THINK: Evidence sufficient? ──
    trace.append({
        "step": "THINK",
        "content": (
            f"Evidence pool: {len(all_sources)} chunks total. "
            f"Internal: {sum(1 for s in all_sources if s.get('source_type')=='internal')}, "
            f"Web: {sum(1 for s in all_sources if s.get('source_type')=='web')}. "
            "Proceeding to generate each section."
        )
    })

    context = build_context_block(all_sources)

    # ── GENERATE: Each section ──
    report_sections = []
    for section_key in sections:
        trace.append({"step": "ACT", "content": f"generate_section({section_key})"})

        prompt = get_section_prompt(section_key, query, context)
        section_content = chat_complete(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=SYSTEM_PROMPT,
            temperature=0.05,
        )

        report_sections.append({
            "section": SECTION_DISPLAY_NAMES.get(section_key, section_key),
            "section_key": section_key,
            "content": section_content,
            "sources": all_sources,    # All sources available for each section
        })

        trace.append({
            "step": "OBSERVE",
            "content": f"Section '{section_key}' generated ({len(section_content)} chars)"
        })
        logger.info(f"  ✓ Section '{section_key}' generated")

    latency_ms = round((time.time() - t0) * 1000, 1)
    logger.info(f"Report generated in {latency_ms}ms | {len(report_sections)} sections")

    return {
        "report_id": report_id,
        "title": title,
        "query": query,
        "sections": report_sections,
        "all_sources": all_sources,
        "generated_at": datetime.utcnow(),
        "latency_ms": latency_ms,
        "trace": trace if include_trace else None,
    }


def settings_top_k() -> int:
    from backend.config import get_settings
    return get_settings().reranker_top_k
