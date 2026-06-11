"""Relationship extraction pipeline for V12.

The pipeline combines deterministic paper metadata ingestion with evidence-based
heuristics.  It is designed as the local fallback behind a production extractor
that may later add embeddings, LLM claim extraction, citation parsers, and human
review queues while preserving the same graph contract.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .graph import KnowledgeGraph
from .schema import EdgeType, NodeType


@dataclass(frozen=True)
class PaperRecord:
    """Normalized paper payload consumed by the extractor."""

    paper_id: str
    title: str
    abstract: str
    authors: tuple[str, ...] = ()
    citations: tuple[str, ...] = ()
    venue: str | None = None
    year: int | None = None


class RelationshipExtractionPipeline:
    """Extract V12 nodes and relationships from paper metadata and text."""

    DATASET_PATTERNS = (
        r"\b(ImageNet|CIFAR-10|CIFAR-100|COCO|SQuAD|GLUE|SuperGLUE|MMLU|HumanEval|GSM8K)\b",
    )
    MODEL_PATTERNS = (
        r"\b(BERT|GPT-\d+(?:\.\d+)?|Transformer|ResNet|LLaMA|T5|ViT|Diffusion Transformer)\b",
    )
    METHOD_PATTERNS = (
        r"\b(chain-of-thought|retrieval augmented generation|RLHF|LoRA|attention|distillation|fine-tuning|contrastive learning)\b",
    )
    BENCHMARK_PATTERNS = (
        r"\b(leaderboard|benchmark|evaluation suite|challenge)[: ]+([A-Z][\w-]+)\b",
    )

    def __init__(self, graph: KnowledgeGraph | None = None) -> None:
        self.graph = graph or KnowledgeGraph()

    def ingest(self, record: PaperRecord | dict[str, Any]) -> KnowledgeGraph:
        """Ingest a paper and extract all supported V12 relationships."""

        paper = self._coerce_record(record)
        self.graph.add_node(
            paper.paper_id,
            NodeType.PAPER,
            title=paper.title,
            abstract=paper.abstract,
            year=paper.year,
        )
        self._extract_authors(paper)
        self._extract_citations(paper)
        self._extract_venue(paper)
        self._extract_entities(paper)
        self._extract_semantic_relationships(paper)
        return self.graph

    def _coerce_record(self, record: PaperRecord | dict[str, Any]) -> PaperRecord:
        if isinstance(record, PaperRecord):
            return record
        return PaperRecord(
            paper_id=str(record["paper_id"]),
            title=str(record["title"]),
            abstract=str(record.get("abstract", "")),
            authors=tuple(record.get("authors", ())),
            citations=tuple(record.get("citations", ())),
            venue=record.get("venue"),
            year=record.get("year"),
        )

    def _extract_authors(self, paper: PaperRecord) -> None:
        for position, name in enumerate(paper.authors, start=1):
            author_id = f"author:{self._slug(name)}"
            self.graph.add_node(author_id, NodeType.AUTHOR, name=name)
            self.graph.add_edge(
                paper.paper_id,
                author_id,
                EdgeType.AUTHORED_BY,
                source="metadata",
                position=position,
                corresponding=position == 1,
            )

    def _extract_citations(self, paper: PaperRecord) -> None:
        for cited_id in paper.citations:
            if cited_id not in self.graph.nodes:
                self.graph.add_node(cited_id, NodeType.PAPER, title=f"Referenced paper {cited_id}")
            self.graph.add_edge(
                paper.paper_id,
                cited_id,
                EdgeType.CITES,
                source="metadata",
                evidence="reference list",
                confidence=0.99,
            )

    def _extract_venue(self, paper: PaperRecord) -> None:
        if not paper.venue:
            return
        venue_id = f"venue:{self._slug(paper.venue)}:{paper.year or 'unknown'}"
        self.graph.add_node(venue_id, NodeType.CONFERENCE, name=paper.venue, year=paper.year)
        self.graph.add_edge(
            paper.paper_id,
            venue_id,
            EdgeType.INSPIRED_BY,
            source="venue-metadata",
            evidence="publication venue context",
            confidence=0.4,
        )

    def _extract_entities(self, paper: PaperRecord) -> None:
        text = f"{paper.title}\n{paper.abstract}"
        for name in self._matches(self.DATASET_PATTERNS, text):
            node_id = f"dataset:{self._slug(name)}"
            self.graph.add_node(node_id, NodeType.DATASET, name=name)
            self.graph.add_edge(paper.paper_id, node_id, EdgeType.EVALUATED_ON, source="text", evidence=name, confidence=0.75)
        for name in self._matches(self.MODEL_PATTERNS, text):
            node_id = f"model:{self._slug(name)}"
            self.graph.add_node(node_id, NodeType.MODEL, name=name)
            self.graph.add_edge(paper.paper_id, node_id, EdgeType.INSPIRED_BY, source="text", evidence=name, confidence=0.55)
        for name in self._matches(self.METHOD_PATTERNS, text):
            node_id = f"method:{self._slug(name)}"
            self.graph.add_node(node_id, NodeType.METHOD, name=name)
            self.graph.add_edge(paper.paper_id, node_id, EdgeType.INSPIRED_BY, source="text", evidence=name, confidence=0.55)
        for _, name in re.findall(self.BENCHMARK_PATTERNS[0], text, flags=re.IGNORECASE):
            node_id = f"benchmark:{self._slug(name)}"
            self.graph.add_node(node_id, NodeType.BENCHMARK, name=name)
            self.graph.add_edge(paper.paper_id, node_id, EdgeType.EVALUATED_ON, source="text", evidence=name, confidence=0.65)

    def _extract_semantic_relationships(self, paper: PaperRecord) -> None:
        text = paper.abstract.lower()
        for cited_id in paper.citations:
            if any(token in text for token in ("outperform", "improve", "state-of-the-art", "better than")):
                self.graph.add_edge(paper.paper_id, cited_id, EdgeType.IMPROVES, source="text", evidence="comparative performance language", confidence=0.7)
            if any(token in text for token in ("contradict", "disagree", "fails to reproduce", "inconsistent with")):
                self.graph.add_edge(paper.paper_id, cited_id, EdgeType.CONTRADICTS, source="text", evidence="contradiction language", confidence=0.65)
            if any(token in text for token in ("inspired by", "builds on", "extends")):
                self.graph.add_edge(paper.paper_id, cited_id, EdgeType.INSPIRED_BY, source="text", evidence="inspiration language", confidence=0.72)

    def _matches(self, patterns: tuple[str, ...], text: str) -> set[str]:
        matches: set[str] = set()
        for pattern in patterns:
            for match in re.findall(pattern, text, flags=re.IGNORECASE):
                value = match if isinstance(match, str) else match[0]
                matches.add(value.strip())
        return matches

    def _slug(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
