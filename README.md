# Arxiv Research Copilot V4

Autonomous multi-agent research copilot for arXiv AI papers. V4 adds agent orchestration, arXiv monitoring, graph memory, ranking, trend detection, daily digests, paper comparison, citation intelligence, flashcards, and research roadmap generation.

## What V4 includes

- Eight-agent research workflow: summarizer, methodology, citation, weakness detector, trend analysis, roadmap, comparison, and flashcard agents.
- LangGraph-ready orchestration with a deterministic local fallback.
- Neo4j graph schema plus offline in-memory graph memory.
- Autonomous daily monitoring for `cs.AI`, `cs.CL`, `cs.LG`, `cs.CV`, and `stat.ML`.
- Importance ranking for daily digests.
- Trend detection for emerging topics and architectures.
- Paper comparison across methods, benchmarks, limitations, and compute costs.
- Research roadmap generation for goals such as “How to learn diffusion models”.
- Notion-ready JSON digest output with a pluggable sink interface.

## Quick start

```bash
python -m pip install -e .
arxiv-copilot-v4 demo --json
arxiv-copilot-v4 roadmap "How to learn diffusion models"
arxiv-copilot-v4 monitor --max-results 25 --top-n 10
```

Optional integrations:

```bash
python -m pip install -e '.[langgraph,neo4j]'
```

## Architecture

See [`docs/v4_architecture.md`](docs/v4_architecture.md) for the graph schema, orchestration layer, autonomous workflow, ranking signals, and scheduling model.
