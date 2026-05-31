"""Domain models for V8 literature-review generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CitationStyle(str, Enum):
    """Supported bibliography and in-text citation styles."""

    APA = "apa"
    IEEE = "ieee"
    MLA = "mla"


@dataclass(frozen=True)
class Paper:
    """A normalized paper record used by the synthesis engine.

    The model intentionally accepts already-summarized inputs as well as raw
    abstracts so workflows can be fed from arXiv exports, curated CSV files, or
    an upstream summarisation stage.
    """

    id: str
    title: str
    authors: tuple[str, ...]
    year: int
    abstract: str
    summary: str = ""
    keywords: tuple[str, ...] = ()
    citations: tuple[str, ...] = ()
    venue: str = ""
    doi: str = ""
    url: str = ""
    claims: tuple[str, ...] = ()
    methods: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def narrative(self) -> str:
        """Return the best available descriptive text for analysis."""

        return " ".join(
            part
            for part in (
                self.title,
                self.summary or self.abstract,
                " ".join(self.keywords),
                " ".join(self.claims),
                " ".join(self.findings),
            )
            if part
        )

    @property
    def lead_author(self) -> str:
        """Return a stable lead-author label for citations."""

        return self.authors[0] if self.authors else "Anonymous"


@dataclass(frozen=True)
class TopicCluster:
    """A thematic cluster produced from a paper collection."""

    id: str
    label: str
    paper_ids: tuple[str, ...]
    keywords: tuple[str, ...]
    summary: str


@dataclass(frozen=True)
class CitationLink:
    """A directed citation edge between two papers in the collection."""

    source_id: str
    target_id: str
    target_in_collection: bool


@dataclass(frozen=True)
class Contradiction:
    """A detected tension or disagreement between papers."""

    paper_ids: tuple[str, str]
    theme: str
    description: str
    confidence: float


@dataclass(frozen=True)
class TrendPoint:
    """Chronological signal for a theme in a publication year."""

    year: int
    theme: str
    paper_ids: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class ReviewSection:
    """A generated section in a structured literature review."""

    title: str
    body: str
    citations: tuple[str, ...]
    paper_ids: tuple[str, ...]


@dataclass(frozen=True)
class ComparisonTable:
    """Markdown-compatible comparison table for the reviewed papers."""

    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    def to_markdown(self) -> str:
        """Render the table as GitHub-flavoured Markdown."""

        header = "| " + " | ".join(self.headers) + " |"
        divider = "| " + " | ".join("---" for _ in self.headers) + " |"
        body = ["| " + " | ".join(row) + " |" for row in self.rows]
        return "\n".join([header, divider, *body])


@dataclass(frozen=True)
class ReviewConfig:
    """Controls deterministic V8 review generation."""

    title: str = "Structured Literature Review"
    citation_style: CitationStyle = CitationStyle.APA
    max_cluster_keywords: int = 6
    min_cluster_size: int = 1
    include_method_table: bool = True
    include_gap_analysis: bool = True
    include_contradictions: bool = True
    include_trends: bool = True


@dataclass(frozen=True)
class Review:
    """Complete V8 literature review artifact."""

    title: str
    sections: tuple[ReviewSection, ...]
    bibliography: tuple[str, ...]
    clusters: tuple[TopicCluster, ...]
    citation_graph: tuple[CitationLink, ...]
    chronology: tuple[TrendPoint, ...]
    contradictions: tuple[Contradiction, ...]
    gaps: tuple[str, ...]
    comparison_tables: tuple[ComparisonTable, ...]

    def to_markdown(self) -> str:
        """Render the review as a single Markdown document."""

        lines = [f"# {self.title}", ""]
        for section in self.sections:
            lines.extend([f"## {section.title}", "", section.body, ""])
        for index, table in enumerate(self.comparison_tables, start=1):
            lines.extend([f"## Comparison Table {index}", "", table.to_markdown(), ""])
        lines.extend(["## Bibliography", ""])
        lines.extend(f"- {entry}" for entry in self.bibliography)
        return "\n".join(lines).strip() + "\n"
