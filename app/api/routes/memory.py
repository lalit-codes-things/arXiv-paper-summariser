from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import build_memory_service, get_session
from app.schemas.memory import MemoryEvent, ReadingHistoryRead, UserProfileRead

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/events", response_model=ReadingHistoryRead)
async def record_memory_event(
    event: MemoryEvent,
    session: AsyncSession = Depends(get_session),
) -> ReadingHistoryRead:
    response = await build_memory_service(session).record_event(event)
    await session.commit()
    return response


@router.get("/users/{user_id}", response_model=UserProfileRead)
async def get_user_memory(user_id: str, session: AsyncSession = Depends(get_session)) -> UserProfileRead:
    return await build_memory_service(session).profile(user_id)
