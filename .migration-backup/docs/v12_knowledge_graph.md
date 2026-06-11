# V12 Global AI Research Knowledge Graph

V12 upgrades the platform from paper summarisation into an interconnected AI
research graph.  The graph links papers, authors, datasets, models, methods,
conferences, and benchmarks so researchers can trace influence, compare claims,
and discover evidence-backed relationships across the literature.

## Graph database schema

The canonical property graph schema is implemented in `arxiv_kg_v12.schema`.
Every node has a stable `id`, a typed label, and searchable metadata.  Every edge
stores provenance through `created_at`, `source`, `confidence`, and optional
relationship-specific evidence.

### Node labels

- `Paper`: research paper or preprint with title, abstract, arXiv id, DOI, year,
  and field metadata.
- `Author`: researcher, lab member, or organization author with ORCID and
  affiliation metadata.
- `Dataset`: dataset or data collection with domain and license metadata.
- `Model`: named AI model, checkpoint, or model family with architecture and
  release metadata.
- `Method`: algorithm, training procedure, loss, or evaluation method.
- `Conference`: conference, workshop, journal, or venue.
- `Benchmark`: benchmark task, leaderboard, metric suite, or challenge.

### Edge types

- `CITES`: a paper cites another paper.
- `IMPROVES`: a paper, model, or method improves a model, method, or benchmark.
- `CONTRADICTS`: a paper disputes another paper or method.
- `INSPIRED_BY`: a paper, model, or method builds on prior research or venue
  context.
- `EVALUATED_ON`: a paper, model, or method is evaluated on a dataset or
  benchmark.
- `AUTHORED_BY`: a paper is authored by an author.

The package can emit Neo4j 5.x constraint and index DDL through
`neo4j_cypher_schema()`.

## Graph traversal APIs

`GraphTraversalAPI` provides product-ready queries:

- `paper_lineage`: traverses citation and inspiration ancestry.
- `author_collaboration_network`: discovers co-authors through shared papers.
- `dataset_usage`: finds research objects evaluated on a dataset.
- `benchmark_leaders`: ranks models, methods, or papers by benchmark score.
- `contradiction_watchlist`: surfaces disputed work.
- `research_influence_score`: combines citations, inspiration, and improvement
  evidence into a lightweight influence score.
- `nodes_by_type`: powers faceted search and graph filtering.

## Graph visualization engine

`GraphVisualizationEngine` exports:

- Cytoscape.js elements for interactive web graph rendering.
- Mermaid flowcharts for markdown, docs, and notebook previews.
- Standalone HTML pages for local exploration and demos.

Nodes are color-coded by schema label, and edge labels preserve relationship
semantics so users can distinguish citations from contradiction, evaluation, and
improvement evidence.

## Relationship extraction pipeline

`RelationshipExtractionPipeline` turns paper metadata and abstract text into graph
updates.  The current deterministic pipeline supports:

1. Metadata ingestion for papers, authors, venues, and references.
2. Citation extraction from normalized reference ids.
3. Entity extraction for common datasets, models, methods, and benchmark names.
4. Semantic relationship extraction for improvement, contradiction, and
   inspiration language.
5. Provenance capture through evidence snippets, confidence scores, and source
   labels.

The implementation is deliberately modular so production deployments can replace
or enrich individual stages with PDF parsers, embedding retrieval, LLM claim
extractors, external registry resolvers, and human review queues while preserving
the V12 graph contract.
