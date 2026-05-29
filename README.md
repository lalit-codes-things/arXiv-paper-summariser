# arXiv-paper-summariser

V8 upgrades the project from single-paper summarisation into a deterministic literature-review platform for paper collections. It can cluster topics, synthesize citation-aware sections, analyze chronology and trend evolution, surface contradictions, identify research gaps, generate comparison tables, and produce a formatted bibliography.

## V8 capabilities

- **Literature synthesis engine**: orchestrates review generation from normalized paper records.
- **Clustering pipeline**: groups papers into thematic topic clusters using lightweight TF-IDF keywords and token-set similarity.
- **Citation-aware synthesis**: preserves in-collection citation links and injects formatted citations into generated review sections.
- **Thematic grouping**: creates one section per discovered theme with evidence snippets.
- **Chronology analysis**: tracks when themes appear and summarizes trend evolution over time.
- **Contradiction detection**: detects likely disagreements from shared concepts with opposing claim polarity.
- **Gap analysis**: highlights sparse themes, explicit limitations, and open challenges.
- **Outputs**: structured Markdown literature reviews, citations, generated sections, bibliography, and comparison tables.

## Install

```bash
python -m pip install -e .
```

## JSON input format

The workflow accepts a JSON list of paper records. Required fields are `id`, `title`, `authors`, `year`, and `abstract`. Optional fields include `summary`, `keywords`, `citations`, `venue`, `doi`, `url`, `claims`, `methods`, `findings`, `limitations`, and `metadata`.

```json
[
  {
    "id": "p1",
    "title": "Neural Retrieval for Scientific Discovery",
    "authors": ["Ada Smith", "Grace Kim"],
    "year": 2020,
    "abstract": "Neural retrieval improves discovery across scientific corpora.",
    "keywords": ["retrieval", "citations"],
    "citations": [],
    "claims": ["retrieval improves discovery"],
    "methods": ["dual encoder"],
    "findings": ["improved citation recommendation"],
    "limitations": ["limited evaluation outside computer science"]
  }
]
```

## Generate a literature review

```bash
arxiv-lit-review papers.json review.md --title "Neural Retrieval Literature Review" --citation-style apa
```

Or use the Python API:

```python
from arxiv_paper_summariser import LiteratureSynthesisEngine, Paper, ReviewConfig

papers = [
    Paper(
        id="p1",
        title="Neural Retrieval for Scientific Discovery",
        authors=("Ada Smith", "Grace Kim"),
        year=2020,
        abstract="Neural retrieval improves discovery across scientific corpora.",
        keywords=("retrieval", "citations"),
    )
]

review = LiteratureSynthesisEngine(ReviewConfig(title="My Review")).generate_review(papers)
print(review.to_markdown())
```

## Development

```bash
python -m pytest
```
