"""Periodic arXiv ingestion worker that can run alongside the main app."""
from __future__ import annotations

import asyncio
import logging

from app.core.database import AsyncSessionLocal
from app.core.dependencies import build_indexing_service
from app.repositories.papers import PaperRepository
from app.services.arxiv_ingestion import ArxivIngestionService

logger = logging.getLogger(__name__)

CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.CV", "stat.ML"]


async def sync_arxiv_once() -> None:
    """Fetch and index recent papers from default arXiv categories."""
    async with AsyncSessionLocal() as session:
        repo = PaperRepository(session)
        service = ArxivIngestionService(repo)
        indexing = build_indexing_service(session)

        for category in CATEGORIES:
            try:
                ids = await service.ingest_category(category, max_results=10)
                logger.info("Ingested %d papers from %s", len(ids), category)

                for paper_id in ids:
                    paper = await repo.get(paper_id)
                    if paper and not paper.chunks:
                        await indexing.index_paper(paper)

                await session.commit()
            except Exception as exc:
                logger.exception("Failed to ingest %s: %s", category, exc)
                await session.rollback()


async def run_arxiv_sync_loop(interval_seconds: int = 3600) -> None:
    """Run arXiv sync on a fixed interval until cancelled."""
    while True:
        logger.info("Starting arXiv sync...")
        await sync_arxiv_once()
        logger.info("arXiv sync complete. Sleeping %ds.", interval_seconds)
        await asyncio.sleep(interval_seconds)
