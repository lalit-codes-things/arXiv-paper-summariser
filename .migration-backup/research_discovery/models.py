"""Core domain models for the V11 research discovery network."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping, Sequence


class InteractionType(str, Enum):
    """Supported user interactions and their recommendation weights."""

    VIEW = "view"
    DWELL = "dwell"
    LIKE = "like"
    SAVE = "save"
    SHARE = "share"
    DISMISS = "dismiss"
    COMPLETE = "complete"

    @property
    def weight(self) -> float:
        return {
            InteractionType.VIEW: 0.05,
            InteractionType.DWELL: 0.18,
            InteractionType.LIKE: 0.42,
            InteractionType.SAVE: 0.72,
            InteractionType.SHARE: 0.85,
            InteractionType.DISMISS: -0.8,
            InteractionType.COMPLETE: 0.95,
        }[self]


@dataclass(frozen=True)
class Paper:
    """A paper available for feed ranking and discovery."""

    paper_id: str
    title: str
    abstract: str
    authors: tuple[str, ...]
    topics: tuple[str, ...]
    conference: str | None = None
    published_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    citation_count: int = 0
    download_count: int = 0
    social_velocity: float = 0.0
    embedding: tuple[float, ...] = field(default_factory=tuple)

    def topic_set(self) -> set[str]:
        return {topic.lower() for topic in self.topics}

    def author_set(self) -> set[str]:
        return {author.lower() for author in self.authors}


@dataclass(frozen=True)
class UserInteraction:
    """A timestamped user event used by personalization memory."""

    user_id: str
    paper_id: str
    interaction_type: InteractionType
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    dwell_seconds: float = 0.0
    topics: tuple[str, ...] = field(default_factory=tuple)
    authors: tuple[str, ...] = field(default_factory=tuple)
    conference: str | None = None


@dataclass
class UserProfile:
    """Mutable personalization state for a reader."""

    user_id: str
    topic_affinity: dict[str, float] = field(default_factory=dict)
    author_affinity: dict[str, float] = field(default_factory=dict)
    conference_affinity: dict[str, float] = field(default_factory=dict)
    subscribed_topics: set[str] = field(default_factory=set)
    tracked_authors: set[str] = field(default_factory=set)
    tracked_conferences: set[str] = field(default_factory=set)
    read_papers: set[str] = field(default_factory=set)
    dismissed_papers: set[str] = field(default_factory=set)
    daily_reads: dict[str, int] = field(default_factory=dict)
    knowledge_progression: dict[str, float] = field(default_factory=dict)

    def normalize_keys(self) -> None:
        """Normalize free-text profile keys for deterministic matching."""

        self.topic_affinity = _normalize_mapping(self.topic_affinity)
        self.author_affinity = _normalize_mapping(self.author_affinity)
        self.conference_affinity = _normalize_mapping(self.conference_affinity)
        self.subscribed_topics = {item.lower() for item in self.subscribed_topics}
        self.tracked_authors = {item.lower() for item in self.tracked_authors}
        self.tracked_conferences = {item.lower() for item in self.tracked_conferences}


def _normalize_mapping(values: Mapping[str, float]) -> dict[str, float]:
    return {key.lower(): value for key, value in values.items()}


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    """Return cosine similarity for sparse-free vectors."""

    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
