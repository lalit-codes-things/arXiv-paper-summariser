from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the V3 backend."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Arxiv Research Copilot"
    api_prefix: str = "/api/v3"
    environment: str = "local"

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/arxiv_copilot",
        description="Async SQLAlchemy URL for PostgreSQL.",
    )
    redis_url: str = "redis://localhost:6379/0"

    vector_backend: Literal["qdrant", "memory"] = "memory"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "arxiv_papers"

    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embedding_batch_size: int = 32

    worker_interval_seconds: int = 60
    max_search_results: int = 25


@lru_cache
def get_settings() -> Settings:
    return Settings()
