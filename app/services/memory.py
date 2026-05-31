from app.repositories.memory import MemoryRepository
from app.repositories.papers import PaperRepository
from app.schemas.memory import MemoryEvent, ReadingHistoryRead, UserProfileRead


class MemoryService:
    def __init__(self, memory: MemoryRepository, papers: PaperRepository):
        self.memory = memory
        self.papers = papers

    async def record_event(self, event: MemoryEvent) -> ReadingHistoryRead:
        paper = await self.papers.get(event.paper_id)
        history = await self.memory.record_view(
            user_id=event.user_id,
            paper_id=event.paper_id,
            action=event.action,
            notes=event.notes,
        )
        if paper is not None:
            await self.memory.update_interests(user_id=event.user_id, topics=paper.topics)
            await self.papers.increment_metric(event.paper_id, "views")
        return ReadingHistoryRead.model_validate(history)

    async def profile(self, user_id: str) -> UserProfileRead:
        return UserProfileRead.model_validate(await self.memory.get_or_create_profile(user_id))
