from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.repositories.memory import MemoryRepository
from app.repositories.papers import PaperRepository, ProcessingJobRepository
from app.services.embeddings import EmbeddingService
from app.services.indexing import IndexingService
from app.services.memory import MemoryService
from app.services.papers import PaperService
from app.services.search import SearchService
from app.services.trending import TrendingService
from app.services.vector_store import VectorStore, create_vector_store

_settings = get_settings()
_embedding_service = EmbeddingService(_settings)
_vector_store = create_vector_store(_settings)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


def get_embedding_service() -> EmbeddingService:
    return _embedding_service


def get_vector_store() -> VectorStore:
    return _vector_store


def get_paper_repository(session: AsyncSession) -> PaperRepository:
    return PaperRepository(session)


def get_processing_job_repository(session: AsyncSession) -> ProcessingJobRepository:
    return ProcessingJobRepository(session)


def build_paper_service(session: AsyncSession) -> PaperService:
    return PaperService(PaperRepository(session), ProcessingJobRepository(session))


def build_search_service(session: AsyncSession, settings: Settings | None = None) -> SearchService:
    resolved_settings = settings or get_settings()
    return SearchService(
        resolved_settings,
        PaperRepository(session),
        get_embedding_service(),
        get_vector_store(),
    )


def build_indexing_service(session: AsyncSession) -> IndexingService:
    return IndexingService(PaperRepository(session), get_embedding_service(), get_vector_store())


def build_memory_service(session: AsyncSession) -> MemoryService:
    return MemoryService(MemoryRepository(session), PaperRepository(session))


def build_trending_service(session: AsyncSession) -> TrendingService:
    return TrendingService(PaperRepository(session))
