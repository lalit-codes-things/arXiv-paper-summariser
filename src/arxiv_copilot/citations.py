"""Citation extraction heuristics."""

from __future__ import annotations

import re

from arxiv_copilot.schemas import Citation

REFERENCES_RE = re.compile(r"(?ims)^references\s*$|^bibliography\s*$")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def extract_citations(text: str, *, max_citations: int = 100) -> list[Citation]:
    """Extract bibliography-like citation entries from plain text."""

    match = REFERENCES_RE.search(text)
    if not match:
        return []
    refs = text[match.end() :]
    entries = _split_reference_entries(refs)
    citations: list[Citation] = []
    for entry in entries[:max_citations]:
        raw = " ".join(entry.split())
        if len(raw) < 20:
            continue
        year_match = YEAR_RE.search(raw)
        title = _guess_title(raw)
        citations.append(Citation(raw=raw, title=title, year=year_match.group(0) if year_match else None, authors=_guess_authors(raw)))
    return citations


def _split_reference_entries(refs: str) -> list[str]:
    lines = [line.strip() for line in refs.splitlines() if line.strip()]
    entries: list[str] = []
    current: list[str] = []
    starter = re.compile(r"^(\[\d+\]|\d+\.|[A-Z][A-Za-z-]+,)")
    for line in lines:
        if current and starter.match(line):
            entries.append(" ".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        entries.append(" ".join(current))
    return entries


def _guess_title(raw: str) -> str | None:
    quoted = re.search(r"[\"“](.+?)[\"”]", raw)
    if quoted:
        return quoted.group(1)
    parts = [part.strip() for part in raw.split(".") if part.strip()]
    return parts[1] if len(parts) > 1 else None


def _guess_authors(raw: str) -> list[str]:
    first = re.sub(r"^\[\d+\]\s*|^\d+\.\s*", "", raw).split(".", 1)[0]
    return [author.strip() for author in re.split(r",\s+|\s+and\s+", first) if author.strip()][:10]
