"""Core domain models used by the V4 agent ecosystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AgentName(str, Enum):
    """Canonical names for the autonomous research agents."""

    SUMMARIZER = "summarizer"
    METHODOLOGY = "methodology"
    CITATION = "citation"
    WEAKNESS_DETECTOR = "weakness_detector"
    TREND_ANALYSIS = "trend_analysis"
    ROADMAP = "research_roadmap"
    PAPER_COMPARISON = "paper_comparison"
    FLASHCARD = "flashcard"


@dataclass(slots=True)
class Paper:
    """Normalized representation of an arXiv paper."""

    paper_id: str
    title: str
    abstract: str
    authors: list[str]
    categories: list[str]
    published: datetime
    updated: datetime | None = None
    url: str | None = None
    pdf_url: str | None = None
    doi: str | None = None
    journal_ref: str | None = None
    comments: str | None = None
    primary_category: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def age_days(self) -> int:
        """Return the whole-day age of the paper relative to now."""

        return max(0, (datetime.now(timezone.utc) - self.published).days)


@dataclass(slots=True)
class AgentResult:
    """Structured output produced by a single agent."""

    agent: AgentName
    paper_id: str | None
    summary: str
    confidence: float
    findings: dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class ComparisonResult:
    """Structured paper comparison result."""

    paper_ids: list[str]
    dimensions: dict[str, dict[str, Any]]
    recommendation: str


@dataclass(slots=True)
class Trend:
    """Detected research trend."""

    name: str
    score: float
    evidence_paper_ids: list[str]
    category: str = "topic"
    rationale: str = ""


@dataclass(slots=True)
class RoadmapStep:
    """One step in a generated research learning path."""

    order: int
    title: str
    objective: str
    paper_ids: list[str] = field(default_factory=list)
    deliverable: str = ""


@dataclass(slots=True)
class DailyDigest:
    """Daily AI research digest payload."""

    date: datetime
    categories: list[str]
    top_papers: list[Paper]
    rankings: dict[str, float]
    trends: list[Trend]
    summaries: dict[str, AgentResult]
    graph_stats: dict[str, int]


@dataclass(slots=True)
class WorkflowResult:
    """Output of a full orchestration run for one or more papers."""

    papers: list[Paper]
    agent_results: list[AgentResult]
    comparisons: list[ComparisonResult] = field(default_factory=list)
    trends: list[Trend] = field(default_factory=list)
    roadmap: list[RoadmapStep] = field(default_factory=list)
    graph_stats: dict[str, int] = field(default_factory=dict)
