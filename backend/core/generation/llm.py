"""
backend/core/generation/llm.py
────────────────────────────────
Groq LLM client with retry logic and token tracking.

Free tier limits (as of 2026):
  - llama-3.3-70b-versatile: 6,000 tokens/min, 500K tokens/day
  - Requests per minute: 30

We handle rate limiting gracefully with tenacity retries.
"""
from __future__ import annotations
from functools import lru_cache
from typing import Any, Generator

from groq import Groq, RateLimitError, APIError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from backend.config import get_settings
from backend.utils.logger import logger

settings = get_settings()


@lru_cache(maxsize=1)
def get_groq_client() -> Groq:
    """Singleton Groq client."""
    client = Groq(api_key=settings.groq_api_key)
    logger.info(f"Groq client initialised | model={settings.groq_model}")
    return client


@retry(
    retry=retry_if_exception_type((RateLimitError,)),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    stop=stop_after_attempt(4),
    reraise=True,
)
def chat_complete(
    messages: list[dict[str, str]],
    system_prompt: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    json_mode: bool = False,
) -> str:
    """
    Single-call LLM completion via Groq.

    Args:
        messages: List of {"role": ..., "content": ...} dicts
        system_prompt: Optional system message (prepended)
        temperature: Override default temperature
        max_tokens: Override default max tokens
        json_mode: If True, forces JSON response format

    Returns:
        Response text string
    """
    client = get_groq_client()

    all_messages = []
    if system_prompt:
        all_messages.append({"role": "system", "content": system_prompt})
    all_messages.extend(messages)

    kwargs: dict[str, Any] = {
        "model": settings.groq_model,
        "messages": all_messages,
        "temperature": temperature if temperature is not None else settings.groq_temperature,
        "max_tokens": max_tokens or settings.groq_max_tokens,
    }

    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content or ""

    logger.debug(
        f"Groq | prompt_tokens={response.usage.prompt_tokens} "
        f"completion_tokens={response.usage.completion_tokens} "
        f"total={response.usage.total_tokens}"
    )
    return content


def build_context_block(chunks: list[dict], max_chars: int = 12000) -> str:
    """
    Format retrieved chunks into a numbered context block for the LLM.

    Truncates to max_chars to stay within context window limits.
    """
    lines = []
    total = 0
    for i, chunk in enumerate(chunks, 1):
        header = (
            f"[SOURCE {i}] File: {chunk.get('filename','?')} | "
            f"Page: {chunk.get('page','?')} | "
            f"Score: {chunk.get('score', 0):.3f}"
        )
        body = chunk.get("content", chunk.get("text", ""))
        entry = f"{header}\n{body}\n"

        if total + len(entry) > max_chars:
            lines.append("[... additional sources truncated for context limit ...]")
            break

        lines.append(entry)
        total += len(entry)

    return "\n".join(lines)
