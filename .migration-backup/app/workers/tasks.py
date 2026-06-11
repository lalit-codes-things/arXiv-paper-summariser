import asyncio
import logging

from app.core.database import AsyncSessionLocal
from app.core.dependencies import build_indexing_service
from app.repositories.papers import PaperRepository, ProcessingJobRepository

logger = logging.getLogger(__name__)


async def process_next_job() -> bool:
    """Claim and execute one queued processing job."""
    async with AsyncSessionLocal() as session:
        jobs = ProcessingJobRepository(session)
        job = await jobs.claim_next()
        if job is None:
            await session.rollback()
            return False
        try:
            papers = PaperRepository(session)
            paper = await papers.get(job.paper_id)
            if paper is None:
                raise ValueError(f"Paper {job.paper_id} not found")
            if job.task_type in {"full_pipeline", "summarize"}:
                paper.summary = paper.summary or _extractive_summary(paper.abstract)
            if job.task_type in {"full_pipeline", "embed", "index"}:
                await build_indexing_service(session).index_paper(paper)
            await jobs.mark_finished(job.id)
            await session.commit()
            return True
        except Exception as exc:
            logger.exception("Processing job %s failed", job.id)
            await jobs.mark_failed(job.id, str(exc))
            await session.commit()
            return False


def run_worker_once() -> None:
    asyncio.run(process_next_job())


def _extractive_summary(text: str, *, max_sentences: int = 3) -> str:
    sentences = [sentence.strip() for sentence in text.replace("\n", " ").split(".") if sentence.strip()]
    return ". ".join(sentences[:max_sentences]) + ("." if sentences else "")
