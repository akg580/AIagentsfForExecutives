"""
backend/utils/validators.py
─────────────────────────────
Input validation helpers used across routes.
Centralises validation logic so routes stay clean.
"""
from __future__ import annotations
from pathlib import Path

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "text/plain",
    "text/markdown",
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt", ".md"}

MAX_QUERY_LENGTH = 2000
MIN_QUERY_LENGTH = 5
MAX_TITLE_LENGTH = 200


def validate_file_extension(filename: str) -> tuple[bool, str]:
    """Check if file extension is allowed."""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        return False, (
            f"File type '{suffix}' not supported. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    return True, ""


def validate_query(query: str) -> tuple[bool, str]:
    """Check query length and basic sanity."""
    q = query.strip()
    if len(q) < MIN_QUERY_LENGTH:
        return False, f"Query too short (min {MIN_QUERY_LENGTH} characters)."
    if len(q) > MAX_QUERY_LENGTH:
        return False, f"Query too long (max {MAX_QUERY_LENGTH} characters)."
    return True, ""


def validate_report_title(title: str) -> tuple[bool, str]:
    """Check report title validity."""
    t = title.strip()
    if len(t) < 3:
        return False, "Report title too short (min 3 characters)."
    if len(t) > MAX_TITLE_LENGTH:
        return False, f"Report title too long (max {MAX_TITLE_LENGTH} characters)."
    return True, ""


def sanitise_filename(filename: str) -> str:
    """Strip unsafe characters from a filename for storage."""
    safe = "".join(
        c if (c.isalnum() or c in "._- ") else "_"
        for c in filename
    )
    return safe[:200].strip()
