from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import build_search_service, build_trending_service, get_session
from app.schemas.paper import RelatedResponse, SearchResponse, TrendingPaper

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(min_length=1),
    limit: int = Query(default=10, ge=1, le=25),
    session: AsyncSession = Depends(get_session),
) -> SearchResponse:
    response = await build_search_service(session).semantic_search(q, limit=limit)
    await session.commit()
    return response


@router.get("/related/{paper_id}", response_model=RelatedResponse)
async def related(
    paper_id: str,
    limit: int = Query(default=10, ge=1, le=25),
    session: AsyncSession = Depends(get_session),
) -> RelatedResponse:
    results = await build_search_service(session).related(paper_id, limit=limit)
    await session.commit()
    return RelatedResponse(paper_id=paper_id, results=results)


@router.get("/trending", response_model=list[TrendingPaper])
async def trending(
    limit: int = Query(default=10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
) -> list[TrendingPaper]:
    return await build_trending_service(session).trending(limit=limit)
