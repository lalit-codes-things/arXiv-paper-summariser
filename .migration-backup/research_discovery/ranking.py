"""Ranking algorithms for feed, trending, and personalized discovery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import exp, log1p
from statistics import mean

from .models import Paper, UserProfile, cosine_similarity


@dataclass(frozen=True)
class RankingWeights:
    """Controls the balance between relevance, freshness, quality, and exploration."""

    topic_match: float = 0.28
    author_match: float = 0.16
    conference_match: float = 0.12
    semantic_match: float = 0.16
    freshness: float = 0.1
    popularity: float = 0.08
    subscriptions: float = 0.08
    knowledge_gap: float = 0.02


@dataclass(frozen=True)
class RankedPaper:
    """A paper enriched with score details for explainable feeds."""

    paper: Paper
    score: float
    reasons: tuple[str, ...]
    components: dict[str, float]


class PaperRanker:
    """Scores papers for TikTok-style swipe feeds and recommendation shelves."""

    def __init__(self, weights: RankingWeights | None = None) -> None:
        self.weights = weights or RankingWeights()

    def rank(
        self,
        profile: UserProfile,
        candidates: list[Paper],
        now: datetime | None = None,
        limit: int | None = None,
    ) -> list[RankedPaper]:
        now = now or datetime.now(timezone.utc)
        ranked = [self.score(profile, paper, now) for paper in candidates]
        ranked = [item for item in ranked if item.paper.paper_id not in profile.dismissed_papers]
        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:limit] if limit is not None else ranked

    def score(self, profile: UserProfile, paper: Paper, now: datetime) -> RankedPaper:
        topic_score = _affinity_overlap(profile.topic_affinity, paper.topics)
        author_score = _affinity_overlap(profile.author_affinity, paper.authors)
        conference_score = _single_affinity(profile.conference_affinity, paper.conference)
        semantic_score = _semantic_profile_score(profile, paper)
        freshness_score = _freshness(paper, now)
        popularity_score = _popularity(paper)
        subscription_score = _subscription_score(profile, paper)
        knowledge_gap_score = _knowledge_gap(profile, paper)

        components = {
            "topic_match": topic_score,
            "author_match": author_score,
            "conference_match": conference_score,
            "semantic_match": semantic_score,
            "freshness": freshness_score,
            "popularity": popularity_score,
            "subscriptions": subscription_score,
            "knowledge_gap": knowledge_gap_score,
        }
        score = sum(getattr(self.weights, key) * value for key, value in components.items())
        if paper.paper_id in profile.read_papers:
            score *= 0.2

        return RankedPaper(
            paper=paper,
            score=round(score, 6),
            reasons=tuple(_reasons(profile, paper, components)),
            components=components,
        )


class TrendingRanker:
    """Ranks globally trending papers using velocity, recency, and quality."""

    def rank(self, papers: list[Paper], now: datetime | None = None, limit: int = 20) -> list[RankedPaper]:
        now = now or datetime.now(timezone.utc)
        ranked = []
        for paper in papers:
            components = {
                "velocity": min(1.0, paper.social_velocity / 100),
                "freshness": _freshness(paper, now),
                "citations": min(1.0, log1p(paper.citation_count) / 10),
                "downloads": min(1.0, log1p(paper.download_count) / 12),
            }
            score = (
                components["velocity"] * 0.46
                + components["freshness"] * 0.26
                + components["citations"] * 0.16
                + components["downloads"] * 0.12
            )
            ranked.append(
                RankedPaper(
                    paper=paper,
                    score=round(score, 6),
                    reasons=("Trending across the research network",),
                    components=components,
                )
            )
        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:limit]


def _affinity_overlap(affinity: dict[str, float], values: tuple[str, ...]) -> float:
    if not affinity or not values:
        return 0.0
    return min(1.0, mean(max(0.0, affinity.get(value.lower(), 0.0)) for value in values) * 3)


def _single_affinity(affinity: dict[str, float], value: str | None) -> float:
    if not value:
        return 0.0
    return min(1.0, max(0.0, affinity.get(value.lower(), 0.0)) * 3)


def _semantic_profile_score(profile: UserProfile, paper: Paper) -> float:
    if not paper.embedding or not profile.topic_affinity:
        return 0.0
    profile_vector = tuple(profile.topic_affinity.get(topic.lower(), 0.0) for topic in paper.topics)
    paper_vector = paper.embedding[: len(profile_vector)]
    return max(0.0, cosine_similarity(profile_vector, paper_vector))


def _freshness(paper: Paper, now: datetime) -> float:
    age_days = max((now - paper.published_at).total_seconds() / 86_400, 0.0)
    return exp(-age_days / 45)


def _popularity(paper: Paper) -> float:
    return min(1.0, (log1p(paper.citation_count) * 0.6 + log1p(paper.download_count) * 0.4) / 10)


def _subscription_score(profile: UserProfile, paper: Paper) -> float:
    score = 0.0
    if profile.subscribed_topics.intersection(paper.topic_set()):
        score += 0.45
    if profile.tracked_authors.intersection(paper.author_set()):
        score += 0.35
    if paper.conference and paper.conference.lower() in profile.tracked_conferences:
        score += 0.2
    return min(1.0, score)


def _knowledge_gap(profile: UserProfile, paper: Paper) -> float:
    if not paper.topics:
        return 0.0
    familiarity = mean(profile.knowledge_progression.get(topic.lower(), 0.0) for topic in paper.topics)
    return max(0.0, 1.0 - min(1.0, familiarity))


def _reasons(profile: UserProfile, paper: Paper, components: dict[str, float]) -> list[str]:
    reasons: list[str] = []
    topic_hits = profile.subscribed_topics.intersection(paper.topic_set())
    author_hits = profile.tracked_authors.intersection(paper.author_set())
    if topic_hits:
        reasons.append(f"Because you subscribe to {', '.join(sorted(topic_hits))}")
    if author_hits:
        reasons.append(f"New work from tracked author {', '.join(sorted(author_hits))}")
    if paper.conference and paper.conference.lower() in profile.tracked_conferences:
        reasons.append(f"From tracked venue {paper.conference}")
    if components["freshness"] > 0.8:
        reasons.append("Recently published")
    if components["popularity"] > 0.6:
        reasons.append("High community engagement")
    if not reasons:
        reasons.append("Explores adjacent research interests")
    return reasons
