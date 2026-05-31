"""Graph traversal APIs for V12 research discovery."""

from __future__ import annotations

from collections import Counter

from .graph import KnowledgeGraph, Node
from .schema import EdgeType, NodeType


class GraphTraversalAPI:
    """High-level graph queries used by product, analytics, and UI layers."""

    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph

    def paper_lineage(self, paper_id: str, depth: int = 2) -> list[str]:
        """Return cited and inspiration ancestors for a paper."""

        frontier = [(paper_id, 0)]
        seen = {paper_id}
        lineage: list[str] = []
        while frontier:
            node_id, current_depth = frontier.pop(0)
            if current_depth >= depth:
                continue
            for _, node in self.graph.neighbors(
                node_id,
                edge_types=(EdgeType.CITES, EdgeType.INSPIRED_BY),
                direction="out",
            ):
                if node.id in seen:
                    continue
                seen.add(node.id)
                lineage.append(node.id)
                frontier.append((node.id, current_depth + 1))
        return lineage

    def author_collaboration_network(self, author_id: str) -> list[Node]:
        """Find authors connected by shared papers."""

        papers = [node for _, node in self.graph.neighbors(author_id, edge_types=(EdgeType.AUTHORED_BY,), direction="in")]
        collaborators: dict[str, Node] = {}
        for paper in papers:
            for _, author in self.graph.neighbors(paper.id, edge_types=(EdgeType.AUTHORED_BY,), direction="out"):
                if author.id != author_id:
                    collaborators[author.id] = author
        return list(collaborators.values())

    def dataset_usage(self, dataset_id: str) -> list[Node]:
        """Return papers, models, and methods evaluated on a dataset."""

        return [node for _, node in self.graph.neighbors(dataset_id, edge_types=(EdgeType.EVALUATED_ON,), direction="in")]

    def benchmark_leaders(self, benchmark_id: str, metric: str | None = None) -> list[tuple[Node, float]]:
        """Rank objects evaluated on a benchmark by numeric score."""

        leaders: list[tuple[Node, float]] = []
        for edge, node in self.graph.neighbors(benchmark_id, edge_types=(EdgeType.EVALUATED_ON,), direction="in"):
            if metric and edge.properties.get("metric") != metric:
                continue
            score = edge.properties.get("score")
            if isinstance(score, int | float):
                leaders.append((node, float(score)))
        return sorted(leaders, key=lambda item: item[1], reverse=True)

    def contradiction_watchlist(self, paper_id: str) -> list[Node]:
        """Return papers or methods that contradict a paper or are contradicted by it."""

        return [node for _, node in self.graph.neighbors(paper_id, edge_types=(EdgeType.CONTRADICTS,), direction="both")]

    def research_influence_score(self, node_id: str) -> float:
        """Compute a lightweight influence score from typed inbound evidence."""

        weights = Counter({EdgeType.CITES: 1.0, EdgeType.INSPIRED_BY: 1.5, EdgeType.IMPROVES: 2.0})
        score = 0.0
        for edge, _ in self.graph.neighbors(node_id, direction="in"):
            score += weights[edge.edge_type] * float(edge.properties.get("confidence", 1.0))
        return score

    def nodes_by_type(self, node_type: NodeType | str) -> list[Node]:
        """Return nodes for a given V12 type."""

        resolved_type = NodeType(node_type)
        return [node for node in self.graph.nodes.values() if node.node_type == resolved_type]
