"""Typed data models for papers, summaries, and processing results."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class PaperMetadata(BaseModel):
    """Metadata returned by arXiv for a research paper."""

    model_config = ConfigDict(frozen=True)

    title: str
    authors: list[str]
    abstract: str
    arxiv_id: str
    pdf_url: HttpUrl
    published: datetime
    categories: list[str]


class PaperSummary(BaseModel):
    """Structured LLM-generated research notes for a paper."""

    tl_dr: str = Field(description="Concise one-paragraph summary of the paper.")
    eli5: str = Field(description="Plain-language explanation for a non-expert reader.")
    technical_summary: str = Field(description="Detailed technical explanation for AI practitioners.")
    key_contributions: list[str] = Field(description="Main scientific or engineering contributions.")
    limitations: list[str] = Field(description="Important caveats, weaknesses, or assumptions.")
    future_work: list[str] = Field(description="Promising follow-up work and research directions.")


class ProcessingResult(BaseModel):
    """End-to-end result produced by the research copilot pipeline."""

    metadata: PaperMetadata
    summary: PaperSummary
