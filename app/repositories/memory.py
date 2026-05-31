from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import ReadingHistory, UserProfile


class MemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_profile(self, user_id: str) -> UserProfile:
        profile = await self.session.get(UserProfile, user_id)
        if profile is None:
            profile = UserProfile(id=user_id)
            self.session.add(profile)
            await self.session.flush()
        return profile

    async def record_view(self, *, user_id: str, paper_id: str, action: str, notes: str | None) -> ReadingHistory:
        await self.get_or_create_profile(user_id)
        stmt = (
            insert(ReadingHistory)
            .values(user_id=user_id, paper_id=paper_id, action=action, notes=notes, viewed_at=datetime.now(UTC))
            .on_conflict_do_update(
                constraint="uq_user_paper_history",
                set_={"action": action, "notes": notes, "viewed_at": datetime.now(UTC)},
            )
            .returning(ReadingHistory)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update_interests(self, *, user_id: str, topics: list[str]) -> UserProfile:
        profile = await self.get_or_create_profile(user_id)
        profile.interests = sorted(set(profile.interests).union(topics))
        clusters = dict(profile.topic_clusters or {})
        for topic in topics:
            clusters[topic] = int(clusters.get(topic, 0)) + 1
        profile.topic_clusters = clusters
        profile.updated_at = datetime.now(UTC)
        await self.session.flush()
        return profile

    async def history(self, user_id: str, *, limit: int = 25) -> list[ReadingHistory]:
        result = await self.session.execute(
            select(ReadingHistory)
            .where(ReadingHistory.user_id == user_id)
            .order_by(ReadingHistory.viewed_at.desc())
            .limit(limit)
        )
        return list(result.scalars())
