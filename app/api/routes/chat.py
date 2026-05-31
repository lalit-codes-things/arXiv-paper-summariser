"""AI-powered paper chat using Anthropic Claude."""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import build_paper_service, get_session

router = APIRouter(prefix="/chat", tags=["chat"])


class PaperChatRequest(BaseModel):
    paper_id: str
    message: str
    conversation_history: list[dict] = Field(default_factory=list)


class PaperChatResponse(BaseModel):
    answer: str
    citations: list[str]
    paper_id: str


@router.post("/paper", response_model=PaperChatResponse)
async def chat_with_paper(
    payload: PaperChatRequest,
    session: AsyncSession = Depends(get_session),
) -> PaperChatResponse:
    paper = await build_paper_service(session).get_paper(payload.paper_id, record_view=False)
    if paper is None:
        raise HTTPException(status_code=404, detail="Paper not found")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return PaperChatResponse(
            answer=f"For '{paper.title}': {paper.abstract[:300]}...",
            citations=[paper.arxiv_id],
            paper_id=payload.paper_id,
        )

    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = f"""You are a research assistant helping a user understand this paper:

Title: {paper.title}
Authors: {', '.join(paper.authors)}
Abstract: {paper.abstract}
Topics: {', '.join(paper.topics)}
{f"Summary: {paper.summary}" if paper.summary else ""}
{f"Methodology: {paper.methodology}" if paper.methodology else ""}

Answer questions about this paper accurately. If you don't know something from the
provided context, say so clearly. Always cite the paper when making claims."""
    messages = payload.conversation_history + [{"role": "user", "content": payload.message}]
    response = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    answer = response.content[0].text
    return PaperChatResponse(answer=answer, citations=[paper.arxiv_id, paper.id], paper_id=payload.paper_id)
