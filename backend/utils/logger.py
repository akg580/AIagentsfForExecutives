"""
backend/utils/logger.py
───────────────────────
Structured logger using loguru. Import `logger` from here everywhere.
"""
import sys
from loguru import logger

logger.remove()  # Remove default handler

logger.add(
    sys.stdout,
    colorize=True,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> — "
        "<level>{message}</level>"
    ),
    level="INFO",
)

logger.add(
    "logs/rag_analyst_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    compression="zip",
    level="DEBUG",
    format="{time} | {level} | {name}:{line} — {message}",
)
