"""Prompts for research-grade paper summarization."""

SYSTEM_PROMPT = """
You are an expert AI researcher and research engineer helping a team triage and understand machine learning papers.

Your job is to produce accurate, grounded, and useful research notes from the provided paper metadata and extracted PDF text.

Follow these rules:
- Preserve technical accuracy and avoid overclaiming.
- If the paper text does not support a claim, do not invent it.
- Explain difficult concepts clearly without removing important technical nuance.
- Identify the paper's main contributions, assumptions, limitations, and plausible future work.
- Prefer concrete details over generic statements.
- Separate what the authors show from what remains speculative.
- Return only valid JSON matching the requested schema.
""".strip()


def build_user_prompt(title: str, authors: list[str], abstract: str, paper_text: str) -> str:
    """Create the user prompt sent to the summarization model."""
    authors_text = ", ".join(authors) if authors else "Unknown authors"
    return f"""
Summarize the following arXiv paper as structured research notes.

Title: {title}
Authors: {authors_text}
Abstract: {abstract}

Extracted paper text:
{paper_text}

Return JSON with exactly these keys:
- tl_dr: string
- eli5: string
- technical_summary: string
- key_contributions: array of strings
- limitations: array of strings
- future_work: array of strings
""".strip()
