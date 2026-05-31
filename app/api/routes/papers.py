from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import build_paper_service, get_session
from app.schemas.paper import PaperCreate, PaperRead, PaperUpdate, ProcessRequest, ProcessResponse

router = APIRouter(tags=["papers"])


@router.get("/papers", response_model=list[PaperRead])
async def list_papers(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    topic: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[PaperRead]:
    papers = await build_paper_service(session).list_papers(limit=limit, offset=offset, topic=topic)
    return [PaperRead.model_validate(paper) for paper in papers]


@router.post("/papers", response_model=PaperRead, status_code=status.HTTP_201_CREATED)
async def upsert_paper(
    payload: PaperCreate,
    session: AsyncSession = Depends(get_session),
) -> PaperRead:
    paper = await build_paper_service(session).upsert_paper(payload)
    await session.commit()
    return PaperRead.model_validate(paper)


@router.get("/paper/{paper_id}", response_model=PaperRead)
async def get_paper(paper_id: str, session: AsyncSession = Depends(get_session)) -> PaperRead:
    paper = await build_paper_service(session).get_paper(paper_id)
    if paper is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
    await session.commit()
    return PaperRead.model_validate(paper)


@router.patch("/paper/{paper_id}", response_model=PaperRead)
async def update_paper(
    paper_id: str,
    payload: PaperUpdate,
    session: AsyncSession = Depends(get_session),
) -> PaperRead:
    paper = await build_paper_service(session).update_paper(paper_id, payload)
    if paper is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
    await session.commit()
    return PaperRead.model_validate(paper)


@router.post("/process", response_model=ProcessResponse, status_code=status.HTTP_202_ACCEPTED)
async def process_papers(
    payload: ProcessRequest,
    session: AsyncSession = Depends(get_session),
) -> ProcessResponse:
    response = await build_paper_service(session).enqueue_processing(payload)
    await session.commit()
    return response
