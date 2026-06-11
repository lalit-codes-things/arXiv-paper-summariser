from pathlib import Path

import pytest

from arxiv_kg_v12 import (
    EdgeType,
    GraphTraversalAPI,
    GraphVisualizationEngine,
    KnowledgeGraph,
    NodeType,
    graph_schema,
    neo4j_cypher_schema,
)
from arxiv_kg_v12.extraction import PaperRecord, RelationshipExtractionPipeline


def test_schema_contains_all_v12_nodes_and_edges():
    schema = graph_schema()

    assert {node["label"] for node in schema["nodes"]} == set(NodeType)
    assert {edge["edge_type"] for edge in schema["edges"]} == set(EdgeType)
    assert "CREATE CONSTRAINT paper_id" in neo4j_cypher_schema()


def test_graph_validation_and_traversal_apis():
    graph = KnowledgeGraph()
    graph.add_node("paper:a", NodeType.PAPER, title="A")
    graph.add_node("paper:b", NodeType.PAPER, title="B")
    graph.add_node("author:ada", NodeType.AUTHOR, name="Ada")
    graph.add_node("dataset:imagenet", NodeType.DATASET, name="ImageNet")
    graph.add_node("benchmark:mmlu", NodeType.BENCHMARK, name="MMLU")
    graph.add_edge("paper:a", "paper:b", EdgeType.CITES)
    graph.add_edge("paper:a", "author:ada", EdgeType.AUTHORED_BY)
    graph.add_edge("paper:a", "dataset:imagenet", EdgeType.EVALUATED_ON, score=91.2, metric="accuracy")
    graph.add_edge("paper:a", "benchmark:mmlu", EdgeType.EVALUATED_ON, score=84.5, metric="accuracy")

    api = GraphTraversalAPI(graph)

    assert api.paper_lineage("paper:a") == ["paper:b"]
    assert [node.id for node in api.dataset_usage("dataset:imagenet")] == ["paper:a"]
    assert api.benchmark_leaders("benchmark:mmlu", metric="accuracy")[0][1] == 84.5
    assert api.research_influence_score("paper:b") == pytest.approx(1.0)


def test_relationship_extraction_pipeline_creates_research_graph():
    pipeline = RelationshipExtractionPipeline()
    graph = pipeline.ingest(
        PaperRecord(
            paper_id="paper:v12",
            title="LoRA improves GPT-4 on benchmark: MMLU",
            abstract="Inspired by prior work, we improve Transformer results on ImageNet and contradict weak baselines.",
            authors=("Ada Lovelace", "Grace Hopper"),
            citations=("paper:prior",),
            venue="ICML",
            year=2026,
        )
    )

    assert "author:ada-lovelace" in graph.nodes
    assert "dataset:imagenet" in graph.nodes
    assert "model:gpt-4" in graph.nodes
    assert "method:lora" in graph.nodes
    assert "benchmark:mmlu" in graph.nodes
    assert {edge.edge_type for edge in graph.edges} >= {
        EdgeType.AUTHORED_BY,
        EdgeType.CITES,
        EdgeType.EVALUATED_ON,
        EdgeType.INSPIRED_BY,
        EdgeType.IMPROVES,
        EdgeType.CONTRADICTS,
    }


def test_visualization_exports(tmp_path: Path):
    graph = KnowledgeGraph()
    graph.add_node("paper:a", NodeType.PAPER, title="A")
    graph.add_node("paper:b", NodeType.PAPER, title="B")
    graph.add_edge("paper:a", "paper:b", EdgeType.CITES)

    engine = GraphVisualizationEngine(graph)
    cytoscape = engine.to_cytoscape()
    html_path = engine.write_html(tmp_path / "graph.html")

    assert cytoscape["nodes"][0]["data"]["type"] == "Paper"
    assert "cites" in engine.to_mermaid()
    assert html_path.exists()
