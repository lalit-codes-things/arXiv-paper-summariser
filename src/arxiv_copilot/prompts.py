"""Prompt templates for structured research summaries."""

from __future__ import annotations

SUMMARY_SCHEMA_INSTRUCTIONS = """
Return valid JSON only. Do not wrap it in Markdown.
Schema keys:
- tl_dr: string
- eli5: string
- technical_summary: string
- methodology: array of strings
- datasets: array of strings
- metrics: array of strings
- contributions: array of strings
- limitations: array of strings
- future_work: array of strings
- flashcards: array of {question, answer, kind, source_section}
- suggested_reading: array of {title, reason, arxiv_id, url, citation_count}
""".strip()


def chunk_summary_prompt(title: str, chunk_index: int, chunk_count: int, text: str) -> str:
    return f"""
You are an expert AI research assistant. Summarize chunk {chunk_index + 1}/{chunk_count} of the paper "{title}".
Focus on facts grounded in this chunk. Capture methods, datasets, metrics, contributions, limitations, future work, and flashcards.
{SUMMARY_SCHEMA_INSTRUCTIONS}

Paper chunk:
{text}
""".strip()


def merge_summary_prompt(title: str, partial_json: str) -> str:
    return f"""
You are merging chunk-level JSON summaries into one coherent paper summary for "{title}".
Deduplicate bullets, preserve important caveats, and produce multi-level summaries suitable for researchers and beginners.
{SUMMARY_SCHEMA_INSTRUCTIONS}

Chunk summaries JSON:
{partial_json}
""".strip()


def single_paper_prompt(title: str, abstract: str, text: str) -> str:
    return f"""
You are an expert AI research assistant. Produce a structured, citation-aware summary for the paper "{title}".
Use the abstract for orientation and the body for evidence. Include concise TL;DR, ELI5, and technical explanations.
{SUMMARY_SCHEMA_INSTRUCTIONS}

Abstract:
{abstract}

Paper text:
{text}
""".strip()
