from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.workers.arxiv_sync import run_arxiv_sync_loop
from app.workers.scheduler import create_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    scheduler = create_scheduler()
    scheduler.start()
    app.state.scheduler = scheduler

    sync_task = asyncio.create_task(run_arxiv_sync_loop(3600))
    app.state.sync_task = sync_task

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        sync_task.cancel()
        try:
            await sync_task
        except asyncio.CancelledError:
            pass


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="3.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "https://arxivcopilot.ai",
            os.getenv("FRONTEND_URL", "http://localhost:3000"),
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    @app.get("/readyz", tags=["system"])
    async def readyz() -> dict[str, str]:
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            return {"status": "ready", "db": "ok"}
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"DB not ready: {exc}") from exc

    return app


app = create_app()
