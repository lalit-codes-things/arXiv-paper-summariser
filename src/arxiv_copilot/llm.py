"""LLM abstraction for structured JSON summaries."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from arxiv_copilot.chunking import PaperChunker
from arxiv_copilot.prompts import chunk_summary_prompt, merge_summary_prompt, single_paper_prompt
from arxiv_copilot.schemas import StructuredSummary
from arxiv_copilot.utils.retry import RetryConfig, retry

LOGGER = logging.getLogger(__name__)


class LLMClient(ABC):
    """Provider-neutral LLM interface."""

    @abstractmethod
    def complete_json(self, prompt: str) -> dict[str, Any]:
        """Return parsed JSON for a prompt."""


@dataclass(slots=True)
class OpenAIJSONClient(LLMClient):
    """OpenAI-backed JSON client loaded lazily to keep base install lightweight."""

    model: str = "gpt-4o-mini"
    api_key: str | None = None
    timeout: float = 60.0
    retry_config: RetryConfig | None = None

    def complete_json(self, prompt: str) -> dict[str, Any]:
        def operation() -> dict[str, Any]:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key, timeout=self.timeout)
            response = client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You return strict JSON for research-paper analysis."},
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)

        return retry(operation, self.retry_config, label="OpenAI structured completion")


@dataclass(slots=True)
class HeuristicLLMClient(LLMClient):
    """Deterministic fallback for tests and offline local runs."""

    def complete_json(self, prompt: str) -> dict[str, Any]:
        first_line = next((line.strip() for line in prompt.splitlines() if line.strip()), "Paper summary")
        return {
            "tl_dr": first_line[:240],
            "eli5": "This paper is explained in simple terms from the available text.",
            "technical_summary": _truncate(prompt, 900),
            "methodology": _extract_lines(prompt, ["method", "approach", "algorithm"]),
            "datasets": _extract_lines(prompt, ["dataset", "benchmark", "corpus"]),
            "metrics": _extract_lines(prompt, ["accuracy", "f1", "auc", "bleu", "rouge", "metric"]),
            "contributions": _extract_lines(prompt, ["contribution", "we propose", "novel"]),
            "limitations": _extract_lines(prompt, ["limitation", "future", "fail"]),
            "future_work": _extract_lines(prompt, ["future work", "future"]),
            "flashcards": [
                {
                    "question": "What is the main idea of this paper?",
                    "answer": first_line[:240],
                    "kind": "qa",
                    "source_section": None,
                }
            ],
            "suggested_reading": [],
        }


@dataclass(slots=True)
class SummarizationEngine:
    """Structured summarizer with chunking and merge support."""

    llm: LLMClient
    chunker: PaperChunker

    def summarize(self, *, title: str, abstract: str, text: str) -> StructuredSummary:
        chunks = self.chunker.chunk(text)
        LOGGER.info("Summarizing %s chunk(s) for %s", len(chunks), title)
        if len(chunks) == 1:
            return StructuredSummary.from_dict(self.llm.complete_json(single_paper_prompt(title, abstract, chunks[0].text)))

        partials = []
        for chunk in chunks:
            prompt = chunk_summary_prompt(title, chunk.index, len(chunks), chunk.text)
            partials.append(self.llm.complete_json(prompt))
        merged = self.llm.complete_json(merge_summary_prompt(title, json.dumps(partials)))
        return StructuredSummary.from_dict(merged)


def _truncate(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    return compact[:limit]


def _extract_lines(text: str, needles: list[str], *, limit: int = 5) -> list[str]:
    found: list[str] = []
    for sentence in text.replace("\n", " ").split("."):
        lowered = sentence.lower()
        if any(needle in lowered for needle in needles):
            item = sentence.strip()
            if item and item not in found:
                found.append(item[:240])
        if len(found) >= limit:
            break
    return found
