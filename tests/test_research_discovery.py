from datetime import datetime, timedelta, timezone

from research_discovery import InteractionType, Paper, PersonalizationMemory, RecommendationEngine, UserInteraction
from research_discovery.ranking import TrendingRanker


NOW = datetime(2026, 5, 28, tzinfo=timezone.utc)


def make_papers():
    return [
        Paper(
            paper_id="p1",
            title="Transformers for Scientific Literature Discovery",
            abstract="Personalized retrieval over research graphs.",
            authors=("Ada Lovelace",),
            topics=("recommendation systems", "nlp"),
            conference="NeurIPS",
            published_at=NOW - timedelta(days=2),
            citation_count=12,
            download_count=500,
            social_velocity=80,
            embedding=(0.9, 0.7),
        ),
        Paper(
            paper_id="p2",
            title="Quantum Error Correction Survey",
            abstract="A broad survey of quantum codes.",
            authors=("Grace Hopper",),
            topics=("quantum computing",),
            conference="QIP",
            published_at=NOW - timedelta(days=20),
            citation_count=50,
            download_count=200,
            social_velocity=20,
            embedding=(0.1,),
        ),
        Paper(
            paper_id="p3",
            title="Graph Neural Networks for Molecules",
            abstract="Molecular property prediction with graph models.",
            authors=("Alan Turing",),
            topics=("graph neural networks", "drug discovery"),
            conference="ICML",
            published_at=NOW - timedelta(days=1),
            citation_count=8,
            download_count=900,
            social_velocity=95,
            embedding=(0.2, 0.4),
        ),
    ]


def test_personalized_recommendations_prioritize_subscriptions_and_memory():
    memory = PersonalizationMemory()
    memory.subscribe_topic("u1", "recommendation systems")
    memory.track_author("u1", "Ada Lovelace")
    memory.track_conference("u1", "NeurIPS")
    memory.record(
        UserInteraction(
            user_id="u1",
            paper_id="seed",
            interaction_type=InteractionType.COMPLETE,
            occurred_at=NOW,
            dwell_seconds=240,
            topics=("recommendation systems", "nlp"),
            authors=("Ada Lovelace",),
            conference="NeurIPS",
        )
    )

    engine = RecommendationEngine(memory)
    ranked = engine.recommend("u1", make_papers(), limit=3)

    assert ranked[0].paper.paper_id == "p1"
    assert ranked[0].components["subscriptions"] > 0
    assert "recommendation systems" in ranked[0].reasons[0]


def test_feed_generation_mixes_discovery_lanes_and_streaks():
    memory = PersonalizationMemory()
    memory.subscribe_topic("u2", "graph neural networks")
    memory.record(
        UserInteraction(
            user_id="u2",
            paper_id="p0",
            interaction_type=InteractionType.COMPLETE,
            occurred_at=datetime.now(timezone.utc),
            topics=("graph neural networks",),
        )
    )

    feed = RecommendationEngine(memory).research_feed("u2", make_papers(), limit=3)

    assert feed.reading_streak == 1
    assert len(feed.items) == 3
    assert {item.lane for item in feed.items}
    assert feed.trending
    assert feed.subscriptions


def test_trending_ranker_uses_velocity_and_freshness():
    ranked = TrendingRanker().rank(make_papers(), now=NOW, limit=2)

    assert ranked[0].paper.paper_id == "p3"
    assert ranked[0].components["velocity"] > ranked[1].components["velocity"]
