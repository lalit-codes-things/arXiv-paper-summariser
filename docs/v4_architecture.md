# Arxiv Research Copilot V4 Architecture

V4 turns the project into an autonomous AI research agent ecosystem inspired by Perplexity AI, Research Rabbit, Semantic Scholar, and NotebookLM.

## Agent ecosystem

The default orchestration stack contains eight agents:

1. **Summarizer Agent** — creates concise TL;DRs and topic summaries.
2. **Methodology Agent** — extracts methods, datasets, benchmarks, and compute signals.
3. **Citation Agent** — uses graph memory to identify related and shared-author papers.
4. **Weakness Detector Agent** — flags likely limitations, weak evaluation evidence, and reproducibility gaps.
5. **Trend Analysis Agent** — finds paper-level trend signals in the monitored cohort.
6. **Research Roadmap Agent** — generates learning steps grounded in papers.
7. **Paper Comparison Agent** — compares methods, benchmarks, limitations, and compute costs.
8. **Flashcard Agent** — creates active-recall study cards.

The orchestrator can run as a deterministic local pipeline or compile into LangGraph when the `langgraph` optional dependency is installed.

## Graph schema

Neo4j graph memory uses these labels:

- `Paper`
- `Author`
- `Topic`
- `Dataset`
- `Method`
- `Category`
- `Digest`
- `Trend`

Relationships:

- `(:Author)-[:AUTHORED]->(:Paper)`
- `(:Paper)-[:HAS_TOPIC]->(:Topic)`
- `(:Paper)-[:USES_DATASET]->(:Dataset)`
- `(:Paper)-[:USES_METHOD]->(:Method)`
- `(:Paper)-[:IN_CATEGORY]->(:Category)`
- `(:Paper)-[:CITES]->(:Paper)`
- `(:Paper)-[:RELATED_TO]->(:Paper)`
- `(:Paper)-[:MENTIONED_IN]->(:Digest)`
- `(:Trend)-[:TRENDING_IN]->(:Category)`
- `(:Paper)-[:COMPARES_WITH]->(:Paper)`

## Autonomous daily monitoring

`DailyMonitoringWorkflow` monitors these default categories:

- `cs.AI`
- `cs.CL`
- `cs.LG`
- `cs.CV`
- `stat.ML`

The workflow fetches recent papers, ingests graph memory, runs all agents, ranks papers, detects trends, and writes a Notion-ready JSON digest. A custom `DigestSink` can push directly to Notion.

## Ranking system

`PaperRanker` combines:

- recency decay,
- target category fit,
- benchmark/evaluation evidence,
- reproducibility signals,
- cohort trend overlap,
- aggregate agent confidence.

## Scheduling

`DailyScheduler` computes the next daily run time and can execute continuously with an injectable `sleep` function for production daemons or tests.
