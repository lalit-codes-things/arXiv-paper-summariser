"""Personalized research feed powered by the research_discovery library."""
from __future__ import annotations

import importlib.util
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session
from app.repositories.papers import PaperRepository

router = APIRouter(prefix="/feed", tags=["feed"])


class FeedPaper(BaseModel):
    id: str
    arxiv_id: str
    title: str
    abstract: str
    authors: list[str]
    topics: list[str]
    score: float
    published_at: datetime | None
    reason: str

    model_config = {"from_attributes": True}


@router.get("/personalized", response_model=list[FeedPaper])
async def personalized_feed(
    user_id: str = Query(default="anonymous"),
    limit: int = Query(default=20, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
) -> list[FeedPaper]:
    """Return a ranked personalized paper feed for a user."""
    repo = PaperRepository(session)
    papers = await repo.list(limit=100)

    if importlib.util.find_spec("research_discovery") is not None:
        from research_discovery import Paper as DiscoveryPaper
        from research_discovery import PersonalizationMemory, RecommendationEngine

        memory = PersonalizationMemory()
        engine = RecommendationEngine(memory)
        discovery_papers = [
            DiscoveryPaper(
                paper_id=p.id,
                title=p.title,
                abstract=p.abstract,
                authors=tuple(p.authors),
                topics=tuple(p.topics),
                published_at=p.published_at or datetime.now(UTC),
            )
            for p in papers
        ]
        ranked = engine.recommend(user_id, discovery_papers, limit=limit)
        paper_map = {p.id: p for p in papers}
        result: list[FeedPaper] = []
        for ranked_paper in ranked:
            paper = paper_map.get(ranked_paper.paper.paper_id)
            if paper is not None:
                result.append(
                    FeedPaper(
                        id=paper.id,
                        arxiv_id=paper.arxiv_id,
                        title=paper.title,
                        abstract=paper.abstract,
                        authors=paper.authors,
                        topics=paper.topics,
                        score=ranked_paper.score,
                        published_at=paper.published_at,
                        reason=(
                            ranked_paper.reasons[0]
                            if ranked_paper.reasons
                            else "Relevant to your interests"
                        ),
                    )
                )
        return result

    return [
        FeedPaper(
            id=p.id,
            arxiv_id=p.arxiv_id,
            title=p.title,
            abstract=p.abstract,
            authors=p.authors,
            topics=p.topics,
            score=1.0,
            published_at=p.published_at,
            reason="Recently published",
        )
        for p in papers[:limit]
    ]
