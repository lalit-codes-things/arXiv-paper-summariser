# arXiv Paper Summariser — V11 Research Discovery Network

V11 upgrades the project from a summariser concept into a personalized AI research discovery network. The platform now includes primitives for TikTok-style paper feeds, trending discovery, personalized recommendations, topic subscriptions, author and conference tracking, reading streaks, and knowledge progression.

## V11 capabilities

- **TikTok-style research feed**: `FeedGenerator` interleaves multiple ranking lanes into a swipeable stream so users get a mix of for-you recommendations, trending papers, subscriptions, and continue-learning suggestions.
- **Trending papers**: `TrendingRanker` combines social velocity, freshness, citations, and downloads to identify papers gaining community momentum.
- **Personalized recommendations**: `RecommendationEngine` exposes a simple facade over memory, ranking, and feed generation.
- **Topic subscriptions**: `PersonalizationMemory.subscribe_topic()` boosts papers that match explicit user interests.
- **Author tracking**: `PersonalizationMemory.track_author()` promotes new work from followed researchers.
- **Conference tracking**: `PersonalizationMemory.track_conference()` prioritizes papers from tracked venues.
- **Reading streaks**: completed and saved papers update daily read counts used by `reading_streak()`.
- **Knowledge progression**: completed papers increase per-topic progression so the feed can surface adjacent knowledge gaps.

## Core modules

| Module | Purpose |
| --- | --- |
| `research_discovery.models` | Domain models for papers, interactions, profiles, and vector similarity. |
| `research_discovery.memory` | Long-term personalization memory, subscriptions, tracking, streaks, and progression. |
| `research_discovery.ranking` | Ranking algorithms for personalized recommendations and global trending papers. |
| `research_discovery.feed` | Feed generation and recommendation engine facade. |

## Example

```python
from research_discovery import InteractionType, Paper, RecommendationEngine, UserInteraction

engine = RecommendationEngine()
engine.memory.subscribe_topic("reader-1", "large language models")
engine.memory.track_author("reader-1", "Yoshua Bengio")
engine.memory.record(
    UserInteraction(
        user_id="reader-1",
        paper_id="seed-paper",
        interaction_type=InteractionType.COMPLETE,
        topics=("large language models", "alignment"),
        authors=("Yoshua Bengio",),
        conference="NeurIPS",
    )
)

papers = [
    Paper(
        paper_id="2401.00001",
        title="Efficient Alignment for Scientific Language Models",
        abstract="A method for aligning models on scientific tasks.",
        authors=("Yoshua Bengio",),
        topics=("large language models", "alignment"),
        conference="NeurIPS",
        citation_count=42,
        download_count=1800,
        social_velocity=73,
    )
]

feed = engine.research_feed("reader-1", papers, limit=10)
print(feed.items[0].reason)
```

## Testing

Run the V11 unit tests with:

```bash
python -m pytest
```
