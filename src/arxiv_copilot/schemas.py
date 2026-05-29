"""Typed data schemas used by Arxiv Research Copilot."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Literal

FlashcardKind = Literal["qa", "concept", "implementation"]


@dataclass(slots=True)
class Flashcard:
    """A generated study card."""

    question: str
    answer: str
    kind: FlashcardKind = "qa"
    source_section: str | None = None


@dataclass(slots=True)
class SuggestedReading:
    """A paper suggestion returned by the LLM or enrichment provider."""

    title: str
    reason: str
    arxiv_id: str | None = None
    url: str | None = None
    citation_count: int | None = None


@dataclass(slots=True)
class StructuredSummary:
    """Canonical V2 JSON output schema."""

    tl_dr: str
    eli5: str
    technical_summary: str
    methodology: list[str] = field(default_factory=list)
    datasets: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)
    contributions: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    future_work: list[str] = field(default_factory=list)
    flashcards: list[Flashcard] = field(default_factory=list)
    suggested_reading: list[SuggestedReading] = field(default_factory=list)

    @classmethod
    def empty(cls) -> "StructuredSummary":
        return cls(tl_dr="", eli5="", technical_summary="")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StructuredSummary":
        flashcards = [
            card if isinstance(card, Flashcard) else Flashcard(**card)
            for card in payload.get("flashcards", [])
        ]
        suggested = [
            item if isinstance(item, SuggestedReading) else SuggestedReading(**item)
            for item in payload.get("suggested_reading", [])
        ]
        data = dict(payload)
        data["flashcards"] = flashcards
        data["suggested_reading"] = suggested
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ArxivPaper:
    """Metadata fetched from arXiv."""

    arxiv_id: str
    title: str
    abstract: str
    authors: list[str]
    published: str | None = None
    updated: str | None = None
    pdf_url: str | None = None
    entry_url: str | None = None
    categories: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Citation:
    """A citation reference extracted from paper text."""

    raw: str
    title: str | None = None
    year: str | None = None
    authors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SemanticScholarPaper:
    """Selected Semantic Scholar enrichment metadata."""

    paper_id: str | None = None
    title: str | None = None
    url: str | None = None
    citation_count: int | None = None
    influential_citation_count: int | None = None
    authors: list[dict[str, Any]] = field(default_factory=list)
    influential_citations: list[dict[str, Any]] = field(default_factory=list)
    related_papers: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class PaperResult:
    """Complete locally storable result for one processed paper."""

    paper: ArxivPaper
    summary: StructuredSummary
    citations: list[Citation] = field(default_factory=list)
    semantic_scholar: SemanticScholarPaper | None = None

    def to_dict(self) -> dict[str, Any]:
        return _to_plain_dict(self)


def _to_plain_dict(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _to_plain_dict(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_to_plain_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_plain_dict(item) for key, item in value.items()}
    return value
