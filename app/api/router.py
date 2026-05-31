from fastapi import APIRouter

from app.api.routes import memory, papers, search

api_router = APIRouter()
api_router.include_router(papers.router)
api_router.include_router(search.router)
api_router.include_router(memory.router)
