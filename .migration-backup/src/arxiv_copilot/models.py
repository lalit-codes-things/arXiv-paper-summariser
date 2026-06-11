"""Typed data models for the first ArXiv Research Copilot milestone.

The project starts deliberately small: one arXiv paper should be normalized into
metadata, extracted notes, a structured summary, and a Notion-ready payload.  The
models in this module are dependency-free dataclasses so the first end-to-end
slice can run in a fresh Python 3.11+ environment before the project adopts a
larger framework such as Pydantic.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class ProcessingStatus(StrEnum):
    """Lifecycle states for a paper moving through the pipeline."""

    DISCOVERED = "discovered"
    METADATA_FETCHED = "metadata_fetched"
    PDF_DOWNLOADED = "pdf_downloaded"
    TEXT_EXTRACTED = "text_extracted"
    SUMMARIZED = "summarized"
    NOTION_SYNCED = "notion_synced"
    FAILED = "failed"


@dataclass(slots=True)
class PaperMetadata:
    """Normalized arXiv metadata for a single paper."""

    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    published_at: datetime
    updated_at: datetime
    categories: list[str]
    primary_category: str
    arxiv_url: str
    pdf_url: str
    doi: str | None = None
    journal_ref: str | None = None
    comment: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the metadata into JSON-friendly primitives."""

        payload = asdict(self)
        payload["published_at"] = self.published_at.isoformat()
        payload["updated_at"] = self.updated_at.isoformat()
        return payload


@dataclass(slots=True)
class PaperSection:
    """A section extracted from a paper PDF or structured parser."""

    title: str
    text: str
    level: int = 1
    page_start: int | None = None
    page_end: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the section into JSON-friendly primitives."""

        return asdict(self)


@dataclass(slots=True)
class PaperReference:
    """A bibliographic reference extracted from the paper."""

    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the reference into JSON-friendly primitives."""

        return asdict(self)


@dataclass(slots=True)
class Flashcard:
    """A study card generated from the paper notes."""

    question: str
    answer: str
    source_section: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the flashcard into JSON-friendly primitives."""

        return asdict(self)


@dataclass(slots=True)
class PaperSummary:
    """Structured notes expected from the LLM summarization step."""

    tl_dr: str
    eli5: str
    technical_summary: str
    core_contributions: list[str] = field(default_factory=list)
    method_breakdown: list[str] = field(default_factory=list)
    datasets: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    reproducibility: list[str] = field(default_factory=list)
    implementation_notes: list[str] = field(default_factory=list)
    flashcards: list[Flashcard] = field(default_factory=list)
    related_papers: list[str] = field(default_factory=list)
    suggested_next_reads: list[str] = field(default_factory=list)
    suggested_code_ideas: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the summary into JSON-friendly primitives."""

        payload = asdict(self)
        payload["flashcards"] = [card.to_dict() for card in self.flashcards]
        return payload


@dataclass(slots=True)
class PaperGraphNode:
    """A future knowledge-graph node for papers, authors, datasets, or topics."""

    node_id: str
    node_type: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the node into JSON-friendly primitives."""

        return asdict(self)


@dataclass(slots=True)
class PaperGraphEdge:
    """A future knowledge-graph edge such as cites, uses_dataset, or same_topic."""

    source_id: str
    target_id: str
    relationship: str
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the edge into JSON-friendly primitives."""

        return asdict(self)


@dataclass(slots=True)
class NotionPagePayload:
    """A Notion-ready representation independent of the Notion HTTP client."""

    title: str
    properties: dict[str, Any]
    blocks: list[dict[str, Any]]
    icon: str | None = "📄"
    cover_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the Notion payload into JSON-friendly primitives."""

        return asdict(self)


@dataclass(slots=True)
class ProcessingResult:
    """The complete local result for processing one paper."""

    status: ProcessingStatus
    metadata: PaperMetadata
    sections: list[PaperSection] = field(default_factory=list)
    references: list[PaperReference] = field(default_factory=list)
    summary: PaperSummary | None = None
    notion_page_id: str | None = None
    raw_pdf_path: str | None = None
    extracted_text_path: str | None = None
    errors: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now().astimezone())
    updated_at: datetime = field(default_factory=lambda: datetime.now().astimezone())

    def to_dict(self) -> dict[str, Any]:
        """Serialize the processing result into JSON-friendly primitives."""

        return {
            "status": self.status.value,
            "metadata": self.metadata.to_dict(),
            "sections": [section.to_dict() for section in self.sections],
            "references": [reference.to_dict() for reference in self.references],
            "summary": self.summary.to_dict() if self.summary else None,
            "notion_page_id": self.notion_page_id,
            "raw_pdf_path": self.raw_pdf_path,
            "extracted_text_path": self.extracted_text_path,
            "errors": self.errors,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
