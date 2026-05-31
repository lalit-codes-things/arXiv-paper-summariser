"""Feed generation system for V11 personalized research discovery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import cycle

from .memory import PersonalizationMemory
from .models import Paper
from .ranking import PaperRanker, RankedPaper, TrendingRanker


@dataclass(frozen=True)
class FeedItem:
    """A card in the swipeable research feed."""

    slot: int
    paper_id: str
    title: str
    authors: tuple[str, ...]
    topics: tuple[str, ...]
    score: float
    reason: str
    lane: str


@dataclass(frozen=True)
class ResearchFeed:
    """A generated feed with shelves for product surfaces."""

    user_id: str
    generated_at: datetime
    items: tuple[FeedItem, ...]
    trending: tuple[FeedItem, ...]
    subscriptions: tuple[FeedItem, ...]
    continue_learning: tuple[FeedItem, ...]
    reading_streak: int


class FeedGenerator:
    """Creates TikTok-style mixed feeds from personalized ranking lanes."""

    def __init__(
        self,
        memory: PersonalizationMemory,
        ranker: PaperRanker | None = None,
        trending_ranker: TrendingRanker | None = None,
    ) -> None:
        self.memory = memory
        self.ranker = ranker or PaperRanker()
        self.trending_ranker = trending_ranker or TrendingRanker()

    def generate(self, user_id: str, papers: list[Paper], limit: int = 30) -> ResearchFeed:
        now = datetime.now(timezone.utc)
        profile = self.memory.get_profile(user_id)
        personalized = self.ranker.rank(profile, papers, now=now)
        trending = self.trending_ranker.rank(papers, now=now, limit=limit)
        subscriptions = [item for item in personalized if item.components["subscriptions"] > 0]
        continue_learning = [
            item for item in personalized if item.components["knowledge_gap"] > 0.35 and item.paper.paper_id not in profile.read_papers
        ]
        mixed = _interleave_lanes(
            {
                "for_you": personalized,
                "trending": trending,
                "subscriptions": subscriptions,
                "continue_learning": continue_learning,
            },
            limit=limit,
        )
        return ResearchFeed(
            user_id=user_id,
            generated_at=now,
            items=tuple(_to_feed_items(mixed)),
            trending=tuple(_to_feed_items(trending[:10], lane="trending")),
            subscriptions=tuple(_to_feed_items(subscriptions[:10], lane="subscriptions")),
            continue_learning=tuple(_to_feed_items(continue_learning[:10], lane="continue_learning")),
            reading_streak=self.memory.reading_streak(user_id, now),
        )


class RecommendationEngine:
    """Facade combining memory updates, ranking, and feed generation."""

    def __init__(self, memory: PersonalizationMemory | None = None) -> None:
        self.memory = memory or PersonalizationMemory()
        self.feed_generator = FeedGenerator(self.memory)

    def recommend(self, user_id: str, papers: list[Paper], limit: int = 10) -> list[RankedPaper]:
        profile = self.memory.get_profile(user_id)
        return self.feed_generator.ranker.rank(profile, papers, limit=limit)

    def research_feed(self, user_id: str, papers: list[Paper], limit: int = 30) -> ResearchFeed:
        return self.feed_generator.generate(user_id, papers, limit=limit)


def _interleave_lanes(lanes: dict[str, list[RankedPaper]], limit: int) -> list[tuple[str, RankedPaper]]:
    lane_order = ("for_you", "for_you", "trending", "subscriptions", "continue_learning")
    lane_cycle = cycle(lane_order)
    indexes = {lane: 0 for lane in lanes}
    seen: set[str] = set()
    output: list[tuple[str, RankedPaper]] = []
    attempts = 0
    max_attempts = max(limit * len(lane_order) * 4, 1)

    while len(output) < limit and attempts < max_attempts:
        lane = next(lane_cycle)
        attempts += 1
        candidates = lanes.get(lane, [])
        index = indexes.get(lane, 0)
        while index < len(candidates) and candidates[index].paper.paper_id in seen:
            index += 1
        indexes[lane] = index + 1
        if index < len(candidates):
            item = candidates[index]
            seen.add(item.paper.paper_id)
            output.append((lane, item))
    return output


def _to_feed_items(items: list[RankedPaper] | list[tuple[str, RankedPaper]], lane: str | None = None) -> list[FeedItem]:
    feed_items: list[FeedItem] = []
    for slot, item in enumerate(items, start=1):
        item_lane, ranked = item if isinstance(item, tuple) else (lane or "for_you", item)
        feed_items.append(
            FeedItem(
                slot=slot,
                paper_id=ranked.paper.paper_id,
                title=ranked.paper.title,
                authors=ranked.paper.authors,
                topics=ranked.paper.topics,
                score=ranked.score,
                reason=ranked.reasons[0],
                lane=item_lane,
            )
        )
    return feed_items
