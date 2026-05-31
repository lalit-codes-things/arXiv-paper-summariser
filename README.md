# arXiv Paper Summariser V12

V12 upgrades the platform into a global interconnected AI research knowledge
graph.  It models research papers, authors, datasets, models, methods,
conferences, and benchmarks as typed nodes, then connects them with evidence-
backed relationships such as citations, improvements, contradictions,
inspiration, evaluations, and authorship.

## Capabilities

- Graph database schema with backend-neutral contracts and Neo4j DDL generation.
- Graph traversal APIs for lineage, collaboration, dataset usage, benchmark
  leaders, contradiction monitoring, and influence scoring.
- Graph visualization engine with Cytoscape.js, Mermaid, and standalone HTML
  exports.
- Relationship extraction pipeline that ingests paper metadata and extracts
  authored-by, cites, improves, contradicts, inspired-by, and evaluated-on edges.

## Quick start

```python
from arxiv_kg_v12 import GraphTraversalAPI, RelationshipExtractionPipeline
from arxiv_kg_v12.extraction import PaperRecord

pipeline = RelationshipExtractionPipeline()
graph = pipeline.ingest(PaperRecord(
    paper_id="paper:v12-demo",
    title="A Transformer Benchmark for Scientific Discovery",
    abstract="We improve prior Transformer results on ImageNet and benchmark: MMLU.",
    authors=("Ada Lovelace", "Grace Hopper"),
    citations=("paper:transformer",),
    venue="NeurIPS",
    year=2026,
))

api = GraphTraversalAPI(graph)
print(api.paper_lineage("paper:v12-demo"))
```

See [docs/v12_knowledge_graph.md](docs/v12_knowledge_graph.md) for the design
and operational model.
