"""OpenAI-compatible LLM summarization client."""

from __future__ import annotations

import json

from openai import OpenAI

from arxiv_copilot.config import Settings
from arxiv_copilot.models import PaperMetadata, PaperSummary
from arxiv_copilot.summarize.prompts import SYSTEM_PROMPT, build_user_prompt


class PaperSummarizer:
    """Generate structured research notes using an OpenAI-compatible model."""

    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for summarization")
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    def summarize(self, metadata: PaperMetadata, paper_text: str) -> PaperSummary:
        """Summarize a paper using its metadata and extracted full text."""
        truncated_text = paper_text[: self.settings.max_paper_text_chars]
        response = self.client.chat.completions.create(
            model=self.settings.openai_model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(
                        title=metadata.title,
                        authors=metadata.authors,
                        abstract=metadata.abstract,
                        paper_text=truncated_text,
                    ),
                },
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM returned an empty summary response")
        return PaperSummary.model_validate(json.loads(content))
