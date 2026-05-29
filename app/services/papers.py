from app.models.paper import Paper
from app.repositories.papers import PaperRepository, ProcessingJobRepository
from app.schemas.paper import PaperCreate, PaperUpdate, ProcessRequest, ProcessResponse


class PaperService:
    def __init__(self, papers: PaperRepository, jobs: ProcessingJobRepository):
        self.papers = papers
        self.jobs = jobs

    async def list_papers(self, *, limit: int, offset: int, topic: str | None = None) -> list[Paper]:
        return await self.papers.list(limit=limit, offset=offset, topic=topic)

    async def get_paper(self, paper_id: str, *, record_view: bool = True) -> Paper | None:
        paper = await self.papers.get(paper_id)
        if paper and record_view:
            await self.papers.increment_metric(paper_id, "views")
        return paper

    async def upsert_paper(self, payload: PaperCreate) -> Paper:
        return await self.papers.upsert(payload)

    async def update_paper(self, paper_id: str, payload: PaperUpdate) -> Paper | None:
        return await self.papers.update(paper_id, payload)

    async def enqueue_processing(self, payload: ProcessRequest) -> ProcessResponse:
        jobs = []
        for paper_id in payload.paper_ids:
            jobs.append(
                await self.jobs.enqueue(
                    paper_id,
                    task_type=payload.task_type,
                    priority=payload.priority,
                )
            )
        return ProcessResponse(queued_jobs=len(jobs), job_ids=[job.id for job in jobs])
