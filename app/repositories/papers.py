from datetime import UTC, datetime

from sqlalchemy import Select, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.paper import Paper, PaperChunk, PaperMetric, ProcessingJob
from app.schemas.paper import PaperCreate, PaperUpdate


class PaperRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, *, limit: int = 50, offset: int = 0, topic: str | None = None) -> list[Paper]:
        stmt: Select = select(Paper).order_by(Paper.created_at.desc()).limit(limit).offset(offset)
        if topic:
            stmt = stmt.where(Paper.topics.contains([topic]))
        result = await self.session.execute(stmt)
        return list(result.scalars().unique())

    async def get(self, paper_id: str) -> Paper | None:
        result = await self.session.execute(
            select(Paper).options(selectinload(Paper.chunks)).where(Paper.id == paper_id)
        )
        return result.scalars().unique().one_or_none()

    async def get_by_arxiv_id(self, arxiv_id: str) -> Paper | None:
        result = await self.session.execute(select(Paper).where(Paper.arxiv_id == arxiv_id))
        return result.scalar_one_or_none()

    async def upsert(self, payload: PaperCreate) -> Paper:
        paper_id = payload.id or payload.arxiv_id
        paper = await self.get(paper_id) or await self.get_by_arxiv_id(payload.arxiv_id)
        values = payload.model_dump(exclude={"metadata"})
        values["paper_metadata"] = payload.metadata
        values["id"] = paper_id
        if paper is None:
            paper = Paper(**values)
            self.session.add(paper)
        else:
            for key, value in values.items():
                setattr(paper, key, value)
        await self.session.flush()
        return paper

    async def update(self, paper_id: str, payload: PaperUpdate) -> Paper | None:
        paper = await self.get(paper_id)
        if paper is None:
            return None
        values = payload.model_dump(exclude_unset=True, exclude={"metadata"})
        if payload.metadata is not None:
            values["paper_metadata"] = payload.metadata
        for key, value in values.items():
            setattr(paper, key, value)
        await self.session.flush()
        return paper

    async def keyword_search(self, query: str, *, limit: int = 10) -> list[Paper]:
        pattern = f"%{query}%"
        result = await self.session.execute(
            select(Paper)
            .where(
                or_(
                    Paper.title.ilike(pattern),
                    Paper.abstract.ilike(pattern),
                    Paper.summary.ilike(pattern),
                    Paper.methodology.ilike(pattern),
                )
            )
            .limit(limit)
        )
        return list(result.scalars().unique())

    async def save_chunks(self, paper_id: str, chunks: list[tuple[str, str, str]]) -> list[PaperChunk]:
        existing = await self.session.execute(select(PaperChunk).where(PaperChunk.paper_id == paper_id))
        for chunk in existing.scalars():
            await self.session.delete(chunk)
        saved: list[PaperChunk] = []
        for chunk_type, content, embedding_id in chunks:
            paper_chunk = PaperChunk(
                paper_id=paper_id,
                chunk_type=chunk_type,
                content=content,
                embedding_id=embedding_id,
                token_count=len(content.split()),
            )
            self.session.add(paper_chunk)
            saved.append(paper_chunk)
        await self.session.flush()
        return saved

    async def increment_metric(self, paper_id: str, field: str) -> None:
        metric = await self.session.get(PaperMetric, paper_id)
        if metric is None:
            metric = PaperMetric(paper_id=paper_id)
            self.session.add(metric)
            await self.session.flush()
        value = getattr(metric, field, 0) + 1
        setattr(metric, field, value)
        metric.last_accessed_at = datetime.now(UTC)

    async def trending(self, *, limit: int = 10) -> list[tuple[Paper, float]]:
        result = await self.session.execute(
            select(Paper, (PaperMetric.views + PaperMetric.searches).label("score"))
            .join(PaperMetric, PaperMetric.paper_id == Paper.id)
            .order_by(func.coalesce(PaperMetric.last_accessed_at, Paper.created_at).desc())
            .limit(limit)
        )
        return [(row[0], float(row[1] or 0)) for row in result.all()]


class ProcessingJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def enqueue(self, paper_id: str, *, task_type: str, priority: int) -> ProcessingJob:
        job = ProcessingJob(paper_id=paper_id, task_type=task_type, priority=priority)
        self.session.add(job)
        await self.session.flush()
        return job

    async def claim_next(self) -> ProcessingJob | None:
        result = await self.session.execute(
            select(ProcessingJob)
            .where(ProcessingJob.status == "queued")
            .order_by(ProcessingJob.priority.asc(), ProcessingJob.queued_at.asc())
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        job = result.scalar_one_or_none()
        if job is None:
            return None
        job.status = "running"
        job.started_at = datetime.now(UTC)
        job.attempts += 1
        await self.session.flush()
        return job

    async def mark_finished(self, job_id: int) -> None:
        await self.session.execute(
            update(ProcessingJob)
            .where(ProcessingJob.id == job_id)
            .values(status="finished", finished_at=datetime.now(UTC), error=None)
        )

    async def mark_failed(self, job_id: int, error: str) -> None:
        await self.session.execute(
            update(ProcessingJob)
            .where(ProcessingJob.id == job_id)
            .values(status="failed", finished_at=datetime.now(UTC), error=error)
        )
