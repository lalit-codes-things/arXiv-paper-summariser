"""Basic smoke tests for core models and prompt construction."""

from __future__ import annotations

from datetime import datetime, timezone

from arxiv_copilot.models import PaperMetadata, PaperSummary, ProcessingResult
from arxiv_copilot.summarize.prompts import SYSTEM_PROMPT, build_user_prompt


def test_models_can_build_processing_result() -> None:
    """The public Pydantic models should compose into a processing result."""
    metadata = PaperMetadata(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani"],
        abstract="A transformer architecture paper.",
        arxiv_id="1706.03762",
        pdf_url="https://arxiv.org/pdf/1706.03762",
        published=datetime(2017, 6, 12, tzinfo=timezone.utc),
        categories=["cs.CL"],
    )
    summary = PaperSummary(
        tl_dr="Introduces the Transformer architecture.",
        eli5="A model can focus on important words instead of reading strictly in order.",
        technical_summary="The paper proposes self-attention layers for sequence transduction.",
        key_contributions=["Scaled dot-product attention", "Multi-head attention"],
        limitations=["High compute cost for long sequences"],
        future_work=["More efficient attention mechanisms"],
    )

    result = ProcessingResult(metadata=metadata, summary=summary)

    assert result.metadata.arxiv_id == "1706.03762"
    assert result.summary.key_contributions[0] == "Scaled dot-product attention"


def test_prompt_requests_grounded_structured_json() -> None:
    """Prompts should ask for grounded structured research notes."""
    user_prompt = build_user_prompt(
        title="Example Paper",
        authors=["Ada Lovelace"],
        abstract="Example abstract.",
        paper_text="Example extracted text.",
    )

    assert "avoid overclaiming" in SYSTEM_PROMPT
    assert "Return JSON" in user_prompt
    assert "key_contributions" in user_prompt
