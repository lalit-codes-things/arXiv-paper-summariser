"""Personalization memory for V11 discovery experiences."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from math import log1p

from .models import InteractionType, UserInteraction, UserProfile


class PersonalizationMemory:
    """Stores and updates reader preferences, subscriptions, and progress."""

    def __init__(self, learning_rate: float = 0.12, decay: float = 0.985) -> None:
        self.learning_rate = learning_rate
        self.decay = decay
        self._profiles: dict[str, UserProfile] = {}
        self._events: dict[str, list[UserInteraction]] = defaultdict(list)

    def get_profile(self, user_id: str) -> UserProfile:
        profile = self._profiles.setdefault(user_id, UserProfile(user_id=user_id))
        profile.normalize_keys()
        return profile

    def subscribe_topic(self, user_id: str, topic: str) -> None:
        self.get_profile(user_id).subscribed_topics.add(topic.lower())

    def track_author(self, user_id: str, author: str) -> None:
        self.get_profile(user_id).tracked_authors.add(author.lower())

    def track_conference(self, user_id: str, conference: str) -> None:
        self.get_profile(user_id).tracked_conferences.add(conference.lower())

    def record(self, event: UserInteraction) -> UserProfile:
        """Apply an interaction event to the user's long-term memory."""

        profile = self.get_profile(event.user_id)
        self._events[event.user_id].append(event)
        signal = event.interaction_type.weight + _dwell_bonus(event)

        for topic in event.topics:
            _bump(profile.topic_affinity, topic, signal, self.learning_rate, self.decay)
            if event.interaction_type is InteractionType.COMPLETE:
                _bump(profile.knowledge_progression, topic, 1.0, self.learning_rate, 1.0)

        for author in event.authors:
            _bump(profile.author_affinity, author, signal, self.learning_rate, self.decay)

        if event.conference:
            _bump(profile.conference_affinity, event.conference, signal, self.learning_rate, self.decay)

        if event.interaction_type in {InteractionType.COMPLETE, InteractionType.SAVE}:
            profile.read_papers.add(event.paper_id)
            day = event.occurred_at.date().isoformat()
            profile.daily_reads[day] = profile.daily_reads.get(day, 0) + 1
        elif event.interaction_type is InteractionType.DISMISS:
            profile.dismissed_papers.add(event.paper_id)

        return profile

    def reading_streak(self, user_id: str, now: datetime | None = None) -> int:
        """Return consecutive days with at least one completed or saved paper."""

        profile = self.get_profile(user_id)
        current = (now or datetime.now(timezone.utc)).date()
        streak = 0
        while profile.daily_reads.get(current.isoformat(), 0) > 0:
            streak += 1
            current -= timedelta(days=1)
        return streak

    def recent_events(self, user_id: str, limit: int = 50) -> list[UserInteraction]:
        return self._events.get(user_id, [])[-limit:]


def _bump(store: dict[str, float], key: str, signal: float, learning_rate: float, decay: float) -> None:
    normalized_key = key.lower()
    store[normalized_key] = store.get(normalized_key, 0.0) * decay + signal * learning_rate


def _dwell_bonus(event: UserInteraction) -> float:
    if event.interaction_type not in {InteractionType.DWELL, InteractionType.COMPLETE}:
        return 0.0
    return min(0.35, log1p(max(event.dwell_seconds, 0.0)) / 20)
