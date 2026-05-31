from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PaperBase(BaseModel):
    arxiv_id: str
    title: str
    abstract: str
    authors: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    contributions: list[str] = Field(default_factory=list)
    methodology: str | None = None
    published_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)


class PaperCreate(PaperBase):
    id: str | None = None
    summary: str | None = None


class PaperUpdate(BaseModel):
    title: str | None = None
    abstract: str | None = None
    summary: str | None = None
    authors: list[str] | None = None
    topics: list[str] | None = None
    contributions: list[str] | None = None
    methodology: str | None = None
    metadata: dict | None = None


class PaperRead(PaperBase):
    metadata: dict = Field(default_factory=dict, validation_alias="paper_metadata")
    id: str
    summary: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaperChunkRead(BaseModel):
    id: int
    paper_id: str
    chunk_type: str
    content: str
    embedding_id: str | None = None

    model_config = {"from_attributes": True}


class ProcessRequest(BaseModel):
    paper_ids: list[str] = Field(default_factory=list)
    force: bool = False
    priority: int = 100
    task_type: Literal["full_pipeline", "summarize", "embed", "index"] = "full_pipeline"


class ProcessResponse(BaseModel):
    queued_jobs: int
    job_ids: list[int]


class SearchResult(BaseModel):
    paper: PaperRead
    score: float
    matched_chunk: str | None = None
    match_type: Literal["semantic", "keyword", "hybrid"] = "semantic"


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class RelatedResponse(BaseModel):
    paper_id: str
    results: list[SearchResult]


class TrendingPaper(BaseModel):
    paper: PaperRead
    score: float
    reason: str
