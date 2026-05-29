# Arxiv Research Copilot

Arxiv Research Copilot turns arXiv papers into structured research notes. V2 extends the original summarizer without changing the core flow: fetch arXiv metadata, download PDFs, extract text, summarize with an LLM, sync optional destinations, and store local JSON.

## V2 capabilities

- **Structured JSON summaries** with typed fields for TL;DR, ELI5, technical summary, methodology, datasets, metrics, contributions, limitations, future work, flashcards, and suggested reading.
- **Long-paper chunking** that tries to preserve section boundaries, avoids token overflow, and merges chunk-level summaries.
- **Retry and resilience** through exponential backoff, request timeouts, and logging.
- **Better prompts** for chunk summaries, merged summaries, and single-paper summaries.
- **Citation extraction** from references and bibliography sections.
- **Semantic Scholar enrichment** for citation counts, influential citations, related papers, and author metadata.
- **Multi-level summaries** for quick reading, beginner explanations, and technical review.
- **Flashcard generation** for Q/A, concept, and implementation cards.
- **Related paper suggestions** from the LLM output and Semantic Scholar recommendations.
- **Batch processing** for multiple arXiv IDs, category feeds, and newest `cs.AI` papers.

## Repository structure

```text
.
├── README.md
├── pyproject.toml
├── src/
│   └── arxiv_copilot/
│       ├── __init__.py
│       ├── arxiv.py
│       ├── citations.py
│       ├── cli.py
│       ├── flashcards.py
│       ├── llm.py
│       ├── notion.py
│       ├── pdf.py
│       ├── pipeline.py
│       ├── prompts.py
│       ├── schemas.py
│       ├── storage.py
│       ├── chunking/
│       │   ├── __init__.py
│       │   └── chunker.py
│       ├── enrich/
│       │   ├── __init__.py
│       │   └── semantic_scholar.py
│       └── utils/
│           ├── __init__.py
│           ├── http.py
│           ├── logging.py
│           └── retry.py
└── tests/
    ├── test_chunking.py
    ├── test_citations_retry.py
    ├── test_pipeline.py
    └── test_schemas_and_llm.py
```

## Installation

```bash
python -m pip install -e .
```

Optional extras:

```bash
python -m pip install -e '.[pdf,llm,dev]'
```

- `pdf` installs `pypdf` for PDF text extraction.
- `llm` installs the OpenAI SDK for real LLM summaries.
- `dev` installs pytest.

## CLI usage

Process one or more arXiv IDs:

```bash
arxiv-copilot --arxiv-id 1706.03762 --arxiv-id 1810.04805
```

Process newest papers in a category:

```bash
arxiv-copilot --category cs.CL --max-results 5
```

Process newest AI papers:

```bash
arxiv-copilot --newest-ai --max-results 10
```

Use abstracts only and disable Semantic Scholar enrichment:

```bash
arxiv-copilot --arxiv-id 1706.03762 --no-pdf --no-semantic-scholar
```

## Python usage

```python
from arxiv_copilot.pipeline import default_pipeline

pipeline = default_pipeline("data")
pipeline.config.download_pdfs = False
result = pipeline.process_arxiv_id("1706.03762")
print(result.summary.tl_dr)
```

## Structured output schema

Every summary is represented by `StructuredSummary` and serialized as JSON:

```json
{
  "tl_dr": "...",
  "eli5": "...",
  "technical_summary": "...",
  "methodology": ["..."],
  "datasets": ["..."],
  "metrics": ["..."],
  "contributions": ["..."],
  "limitations": ["..."],
  "future_work": ["..."],
  "flashcards": [
    {"question": "...", "answer": "...", "kind": "qa", "source_section": "..."}
  ],
  "suggested_reading": [
    {"title": "...", "reason": "...", "arxiv_id": "...", "url": "...", "citation_count": 0}
  ]
}
```

## Notes on providers

The package ships with a deterministic `HeuristicLLMClient` for tests and offline development. Use `OpenAIJSONClient` when you want real model output. Semantic Scholar enrichment uses the public Graph API and accepts an optional API key through `SemanticScholarClient(api_key="...")`.

## Testing

```bash
pytest
```
