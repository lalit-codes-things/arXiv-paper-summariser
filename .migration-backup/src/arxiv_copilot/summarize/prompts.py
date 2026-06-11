"""Prompt templates for structured arXiv paper notes.

These prompts define the first summarization contract before any provider-specific
LLM client exists.  The JSON shape mirrors ``PaperSummary`` so downstream Notion
export can be implemented without prompt rewrites.
"""

from __future__ import annotations

import json
from textwrap import dedent

from arxiv_copilot.models import PaperMetadata

SUMMARY_JSON_SCHEMA: dict[str, object] = {
    "tl_dr": "string",
    "eli5": "string",
    "technical_summary": "string",
    "core_contributions": ["string"],
    "method_breakdown": ["string"],
    "datasets": ["string"],
    "metrics": ["string"],
    "limitations": ["string"],
    "reproducibility": ["string"],
    "implementation_notes": ["string"],
    "flashcards": [
        {"question": "string", "answer": "string", "source_section": "string|null"}
    ],
    "related_papers": ["string"],
    "suggested_next_reads": ["string"],
    "suggested_code_ideas": ["string"],
}

SYSTEM_PROMPT = dedent("""
    You are an expert AI research assistant. Read arXiv papers carefully and
    produce accurate, structured research notes. Ground every claim in the paper
    text. If the paper does not provide enough evidence for a field, return an
    empty list or say "Not specified" instead of guessing.
    """).strip()

SHORT_SUMMARY_PROMPT = "Write a concise TL;DR of the paper in 2-3 sentences."
STUDENT_FRIENDLY_PROMPT = (
    "Explain the paper for a motivated undergraduate in plain language."
)
TECHNICAL_SUMMARY_PROMPT = (
    "Summarize the method, experiments, and findings for an ML researcher."
)
EXPLAIN_MATH_PROMPT = (
    "Extract and explain the main mathematical objects, assumptions, and equations."
)
EXTRACT_METHOD_PROMPT = (
    "Break down the proposed method into ordered implementation steps."
)
LIST_LIMITATIONS_PROMPT = "List explicit and likely limitations, separating stated limitations from inferred ones."
GENERATE_FLASHCARDS_PROMPT = (
    "Generate question-answer flashcards that test the paper's core ideas."
)
GENERATE_CODE_SKELETON_PROMPT = (
    "Suggest a minimal code skeleton for reproducing the method."
)
COMPARE_RELATED_WORKS_PROMPT = (
    "Compare this work with related papers mentioned in the text."
)


def build_structured_summary_prompt(
    metadata: PaperMetadata, paper_text: str, *, max_chars: int = 80_000
) -> str:
    """Build the user prompt for producing a ``PaperSummary`` JSON object."""

    clipped_text = paper_text[:max_chars]
    truncated_note = (
        "\n\n[Note: paper text was truncated for context length.]"
        if len(paper_text) > max_chars
        else ""
    )
    schema = json.dumps(SUMMARY_JSON_SCHEMA, indent=2)
    metadata_json = json.dumps(metadata.to_dict(), indent=2)

    return dedent(f"""
        Create structured research notes for this arXiv paper.

        Metadata:
        {metadata_json}

        Return valid JSON only. Do not wrap it in Markdown. The JSON must match
        this shape exactly, using empty arrays where information is unavailable:
        {schema}

        Required analysis passes:
        1. {SHORT_SUMMARY_PROMPT}
        2. {STUDENT_FRIENDLY_PROMPT}
        3. {TECHNICAL_SUMMARY_PROMPT}
        4. {EXPLAIN_MATH_PROMPT}
        5. {EXTRACT_METHOD_PROMPT}
        6. {LIST_LIMITATIONS_PROMPT}
        7. {GENERATE_FLASHCARDS_PROMPT}
        8. {GENERATE_CODE_SKELETON_PROMPT}
        9. {COMPARE_RELATED_WORKS_PROMPT}

        Paper text:
        {clipped_text}{truncated_note}
        """).strip()
