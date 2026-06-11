from fastapi import APIRouter

from app.api.routes import chat, feed, ingest, memory, papers, search

api_router = APIRouter()
api_router.include_router(papers.router)
api_router.include_router(search.router)
api_router.include_router(memory.router)
api_router.include_router(ingest.router)
api_router.include_router(chat.router)
api_router.include_router(feed.router)
