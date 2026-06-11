"""Research graph schema, graph memory, and Neo4j persistence helpers."""

from __future__ import annotations

import importlib.util
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from .models import Paper
from .text import keywords, keyphrases


@dataclass(frozen=True, slots=True)
class GraphSchema:
    """Neo4j schema for paper, author, topic, dataset, method, citation, and digest intelligence."""

    node_labels: tuple[str, ...] = ("Paper", "Author", "Topic", "Dataset", "Method", "Category", "Digest", "Trend")
    relationship_types: tuple[str, ...] = (
        "AUTHORED", "HAS_TOPIC", "USES_DATASET", "USES_METHOD", "IN_CATEGORY", "CITES",
        "RELATED_TO", "MENTIONED_IN", "TRENDING_IN", "COMPARES_WITH",
    )

    def constraints(self) -> list[str]:
        """Return Cypher statements for idempotent Neo4j constraints and indexes."""

        return [
            "CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (p:Paper) REQUIRE p.paper_id IS UNIQUE",
            "CREATE CONSTRAINT author_name IF NOT EXISTS FOR (a:Author) REQUIRE a.name IS UNIQUE",
            "CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE",
            "CREATE CONSTRAINT dataset_name IF NOT EXISTS FOR (d:Dataset) REQUIRE d.name IS UNIQUE",
            "CREATE CONSTRAINT method_name IF NOT EXISTS FOR (m:Method) REQUIRE m.name IS UNIQUE",
            "CREATE INDEX paper_published IF NOT EXISTS FOR (p:Paper) ON (p.published)",
            "CREATE INDEX trend_score IF NOT EXISTS FOR (t:Trend) ON (t.score)",
        ]

    def paper_upsert_cypher(self) -> str:
        """Return Cypher used by the Neo4j sink to upsert paper neighborhoods."""

        return """
        MERGE (p:Paper {paper_id: $paper_id})
        SET p.title = $title, p.abstract = $abstract, p.url = $url,
            p.published = datetime($published), p.primary_category = $primary_category
        WITH p
        UNWIND $authors AS author_name
          MERGE (a:Author {name: author_name})
          MERGE (a)-[:AUTHORED]->(p)
        WITH p
        UNWIND $categories AS category_name
          MERGE (c:Category {name: category_name})
          MERGE (p)-[:IN_CATEGORY]->(c)
        WITH p
        UNWIND $topics AS topic_name
          MERGE (t:Topic {name: topic_name})
          MERGE (p)-[:HAS_TOPIC]->(t)
        WITH p
        UNWIND $methods AS method_name
          MERGE (m:Method {name: method_name})
          MERGE (p)-[:USES_METHOD]->(m)
        """.strip()


@dataclass(slots=True)
class InMemoryResearchGraph:
    """Graph memory used by local tests, offline runs, and LangGraph state."""

    papers: dict[str, Paper] = field(default_factory=dict)
    edges: dict[str, set[tuple[str, str]]] = field(default_factory=lambda: defaultdict(set))
    topics: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    authors: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    def ingest_paper(self, paper: Paper) -> None:
        """Insert a paper and derive author/topic/method relationships."""

        self.papers[paper.paper_id] = paper
        for author in paper.authors:
            self.authors[author].add(paper.paper_id)
            self.edges["AUTHORED"].add((author, paper.paper_id))
        for category in paper.categories:
            self.edges["IN_CATEGORY"].add((paper.paper_id, category))
        for topic in keywords(paper.title + " " + paper.abstract, limit=10):
            self.topics[topic].add(paper.paper_id)
            self.edges["HAS_TOPIC"].add((paper.paper_id, topic))
        for method, _ in keyphrases(paper.abstract, limit=5):
            self.edges["USES_METHOD"].add((paper.paper_id, method))
        self._connect_related(paper)

    def related_papers(self, paper_id: str, *, limit: int = 10) -> list[str]:
        """Return papers related by shared authors, topics, or categories."""

        scores: defaultdict[str, int] = defaultdict(int)
        paper = self.papers.get(paper_id)
        if paper is None:
            return []
        for author in paper.authors:
            for candidate_id in self.authors.get(author, set()):
                if candidate_id != paper_id:
                    scores[candidate_id] += 3
        for topic in keywords(paper.title + " " + paper.abstract, limit=10):
            for candidate_id in self.topics.get(topic, set()):
                if candidate_id != paper_id:
                    scores[candidate_id] += 1
        return [candidate_id for candidate_id, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True)[:limit]]

    def stats(self) -> dict[str, int]:
        """Return graph memory counts."""

        return {
            "papers": len(self.papers),
            "authors": len(self.authors),
            "topics": len(self.topics),
            "edges": sum(len(values) for values in self.edges.values()),
        }

    def _connect_related(self, paper: Paper) -> None:
        for other_id in self.related_papers(paper.paper_id, limit=20):
            self.edges["RELATED_TO"].add((paper.paper_id, other_id))


class Neo4jSink:
    """Optional Neo4j writer. Requires installing the `neo4j` extra."""

    def __init__(self, uri: str, username: str, password: str, *, schema: GraphSchema | None = None) -> None:
        if importlib.util.find_spec("neo4j") is None:
            raise RuntimeError("Install the neo4j extra to use Neo4jSink: pip install .[neo4j]")
        from neo4j import GraphDatabase

        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.schema = schema or GraphSchema()

    def initialize(self) -> None:
        """Create graph constraints and indexes."""

        with self.driver.session() as session:
            for statement in self.schema.constraints():
                session.run(statement)

    def ingest_paper(self, paper: Paper) -> None:
        """Upsert one paper and its relationships."""

        payload: dict[str, Any] = {
            "paper_id": paper.paper_id,
            "title": paper.title,
            "abstract": paper.abstract,
            "url": paper.url,
            "published": paper.published.isoformat(),
            "primary_category": paper.primary_category or (paper.categories[0] if paper.categories else None),
            "authors": paper.authors,
            "categories": paper.categories,
            "topics": keywords(paper.title + " " + paper.abstract, limit=10),
            "methods": [phrase for phrase, _ in keyphrases(paper.abstract, limit=5)],
        }
        with self.driver.session() as session:
            session.run(self.schema.paper_upsert_cypher(), payload)

    def close(self) -> None:
        """Close the Neo4j driver."""

        self.driver.close()
