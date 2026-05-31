from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import build_indexing_service, get_session
from app.repositories.papers import PaperRepository
from app.services.arxiv_ingestion import ArxivIngestionService

router = APIRouter(prefix="/ingest", tags=["ingestion"])


class IngestCategoryRequest(BaseModel):
    category: str = "cs.AI"
    max_results: int = Field(default=20, ge=1, le=100)
    index: bool = True


class IngestByIdRequest(BaseModel):
    arxiv_id: str
    index: bool = True


@router.post("/category")
async def ingest_category(
    payload: IngestCategoryRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    repo = PaperRepository(session)
    service = ArxivIngestionService(repo)
    ids = await service.ingest_category(payload.category, payload.max_results)
    if payload.index:
        indexing = build_indexing_service(session)
        for paper_id in ids:
            paper = await repo.get(paper_id)
            if paper is not None:
                await indexing.index_paper(paper)
    await session.commit()
    return {"ingested": len(ids), "paper_ids": ids}


@router.post("/paper")
async def ingest_paper(
    payload: IngestByIdRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    repo = PaperRepository(session)
    service = ArxivIngestionService(repo)
    try:
        paper_id = await service.ingest_by_id(payload.arxiv_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if payload.index:
        paper = await repo.get(paper_id)
        if paper is not None:
            await build_indexing_service(session).index_paper(paper)
    await session.commit()
    return {"paper_id": paper_id, "arxiv_id": payload.arxiv_id}


@router.get("/category")
async def ingest_category_get(
    category: str = Query(default="cs.AI"),
    max_results: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> dict:
    return await ingest_category(
        IngestCategoryRequest(category=category, max_results=max_results),
        session,
    )
