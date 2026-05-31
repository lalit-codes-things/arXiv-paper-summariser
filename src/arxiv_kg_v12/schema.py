"""Graph database schema for V12.

The schema is intentionally backend-neutral and can be projected into Neo4j,
Memgraph, ArangoDB, Neptune, or a local in-memory graph.  Neo4j DDL is provided
because Cypher constraints and indexes are a compact, portable baseline for
property graph deployments.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final


class NodeType(StrEnum):
    """Canonical V12 research knowledge graph node labels."""

    PAPER = "Paper"
    AUTHOR = "Author"
    DATASET = "Dataset"
    MODEL = "Model"
    METHOD = "Method"
    CONFERENCE = "Conference"
    BENCHMARK = "Benchmark"


class EdgeType(StrEnum):
    """Canonical V12 semantic relationship types."""

    CITES = "CITES"
    IMPROVES = "IMPROVES"
    CONTRADICTS = "CONTRADICTS"
    INSPIRED_BY = "INSPIRED_BY"
    EVALUATED_ON = "EVALUATED_ON"
    AUTHORED_BY = "AUTHORED_BY"


@dataclass(frozen=True)
class NodeSpec:
    """Schema contract for one node label."""

    label: NodeType
    required: tuple[str, ...]
    indexed: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class EdgeSpec:
    """Schema contract for one relationship type."""

    edge_type: EdgeType
    allowed_sources: tuple[NodeType, ...]
    allowed_targets: tuple[NodeType, ...]
    properties: tuple[str, ...]
    description: str


NODE_SPECS: Final[tuple[NodeSpec, ...]] = (
    NodeSpec(NodeType.PAPER, ("id", "title"), ("arxiv_id", "doi", "year", "field"), "Research paper or preprint."),
    NodeSpec(NodeType.AUTHOR, ("id", "name"), ("orcid", "affiliation"), "Researcher, lab member, or organization author."),
    NodeSpec(NodeType.DATASET, ("id", "name"), ("domain", "license"), "Dataset or data collection used by AI systems."),
    NodeSpec(NodeType.MODEL, ("id", "name"), ("architecture", "release_year"), "Named AI model, checkpoint, or family."),
    NodeSpec(NodeType.METHOD, ("id", "name"), ("category",), "Algorithm, training procedure, loss, or evaluation method."),
    NodeSpec(NodeType.CONFERENCE, ("id", "name"), ("acronym", "year"), "Conference, workshop, journal, or venue."),
    NodeSpec(NodeType.BENCHMARK, ("id", "name"), ("domain", "metric"), "Benchmark task, leaderboard, metric suite, or challenge."),
)

EDGE_SPECS: Final[tuple[EdgeSpec, ...]] = (
    EdgeSpec(EdgeType.CITES, (NodeType.PAPER,), (NodeType.PAPER,), ("evidence", "confidence", "section"), "Paper cites another paper."),
    EdgeSpec(EdgeType.IMPROVES, (NodeType.PAPER, NodeType.MODEL, NodeType.METHOD), (NodeType.PAPER, NodeType.MODEL, NodeType.METHOD, NodeType.BENCHMARK), ("metric", "delta", "evidence", "confidence"), "Work improves a model, method, or benchmark result."),
    EdgeSpec(EdgeType.CONTRADICTS, (NodeType.PAPER,), (NodeType.PAPER, NodeType.METHOD), ("claim", "evidence", "confidence"), "Paper disputes a claim or method from another work."),
    EdgeSpec(EdgeType.INSPIRED_BY, (NodeType.PAPER, NodeType.MODEL, NodeType.METHOD), (NodeType.PAPER, NodeType.MODEL, NodeType.METHOD, NodeType.CONFERENCE), ("evidence", "confidence"), "Research object is inspired by prior research."),
    EdgeSpec(EdgeType.EVALUATED_ON, (NodeType.PAPER, NodeType.MODEL, NodeType.METHOD), (NodeType.DATASET, NodeType.BENCHMARK), ("split", "metric", "score", "evidence", "confidence"), "Research object is evaluated on a dataset or benchmark."),
    EdgeSpec(EdgeType.AUTHORED_BY, (NodeType.PAPER,), (NodeType.AUTHOR,), ("position", "corresponding"), "Paper authored by a person or organization."),
)


def graph_schema() -> dict[str, object]:
    """Return a serializable schema document for API, migrations, and docs."""

    return {
        "version": "12.0.0",
        "nodes": [spec.__dict__ for spec in NODE_SPECS],
        "edges": [spec.__dict__ for spec in EDGE_SPECS],
        "required_edge_properties": ("created_at", "source", "confidence"),
    }


def neo4j_cypher_schema() -> str:
    """Generate Neo4j 5.x constraint/index DDL for the V12 graph."""

    statements: list[str] = []
    for spec in NODE_SPECS:
        label = spec.label.value
        statements.append(
            f"CREATE CONSTRAINT {label.lower()}_id IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE n.id IS UNIQUE;"
        )
        for prop in spec.indexed:
            statements.append(
                f"CREATE INDEX {label.lower()}_{prop} IF NOT EXISTS "
                f"FOR (n:{label}) ON (n.{prop});"
            )
    for spec in EDGE_SPECS:
        rel = spec.edge_type.value.lower()
        statements.append(
            f"CREATE INDEX {rel}_confidence IF NOT EXISTS "
            f"FOR ()-[r:{spec.edge_type.value}]-() ON (r.confidence);"
        )
    return "\n".join(statements)
