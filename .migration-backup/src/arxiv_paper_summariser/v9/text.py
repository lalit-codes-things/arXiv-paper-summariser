"""Text normalization helpers for rule-based paper analysis."""

from __future__ import annotations

import re

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
_HEADING_RE = re.compile(r"^(?:\d+(?:\.\d+)*\s+)?([A-Z][A-Za-z0-9 /:_-]{2,80})$", re.MULTILINE)


def normalize_whitespace(text: str) -> str:
    """Collapse noisy PDF whitespace while preserving paragraph boundaries."""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sentences(text: str) -> list[str]:
    """Split text into implementation-useful sentences."""

    clean = normalize_whitespace(text).replace("\n", " ")
    return [part.strip() for part in _SENTENCE_RE.split(clean) if part.strip()]


def headings(text: str) -> list[str]:
    """Return candidate section headings from paper text."""

    return [match.group(1).strip() for match in _HEADING_RE.finditer(text)]


def slugify(value: str) -> str:
    """Create a stable Python and file-name friendly slug."""

    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "paper_model"


def unique_preserve_order(values: list[str]) -> list[str]:
    """Deduplicate a list without changing first-seen order."""

    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        key = value.lower()
        if key not in seen:
            unique.append(value)
            seen.add(key)
    return unique
