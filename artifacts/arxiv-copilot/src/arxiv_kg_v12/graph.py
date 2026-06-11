"""In-memory graph store used by V12 traversal APIs and tests."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable

from .schema import EDGE_SPECS, NODE_SPECS, EdgeType, NodeType


@dataclass(frozen=True)
class Node:
    """A typed knowledge graph node."""

    id: str
    node_type: NodeType
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    """A typed directed relationship with provenance metadata."""

    source_id: str
    target_id: str
    edge_type: EdgeType
    properties: dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    """Small directed property graph with V12 schema validation."""

    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self._outgoing: dict[str, list[Edge]] = defaultdict(list)
        self._incoming: dict[str, list[Edge]] = defaultdict(list)

    def add_node(self, node_id: str, node_type: NodeType | str, **properties: Any) -> Node:
        """Add or update a node after validating required properties."""

        resolved_type = NodeType(node_type)
        properties = {"id": node_id, **properties}
        spec = next(item for item in NODE_SPECS if item.label == resolved_type)
        missing = [prop for prop in spec.required if prop not in properties]
        if missing:
            raise ValueError(f"Missing required {resolved_type.value} properties: {', '.join(missing)}")
        node = Node(node_id, resolved_type, properties)
        self.nodes[node_id] = node
        return node

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType | str,
        confidence: float = 1.0,
        source: str = "manual",
        **properties: Any,
    ) -> Edge:
        """Add a directed relationship after validating endpoints and type rules."""

        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Both source and target nodes must exist before adding an edge")
        resolved_type = EdgeType(edge_type)
        spec = next(item for item in EDGE_SPECS if item.edge_type == resolved_type)
        source_node = self.nodes[source_id]
        target_node = self.nodes[target_id]
        if source_node.node_type not in spec.allowed_sources:
            raise ValueError(f"{source_node.node_type.value} cannot source {resolved_type.value}")
        if target_node.node_type not in spec.allowed_targets:
            raise ValueError(f"{target_node.node_type.value} cannot target {resolved_type.value}")
        edge_props = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "confidence": confidence,
            **properties,
        }
        edge = Edge(source_id, target_id, resolved_type, edge_props)
        self.edges.append(edge)
        self._outgoing[source_id].append(edge)
        self._incoming[target_id].append(edge)
        return edge

    def neighbors(
        self,
        node_id: str,
        edge_types: Iterable[EdgeType | str] | None = None,
        direction: str = "out",
    ) -> list[tuple[Edge, Node]]:
        """Return adjacent nodes reachable from a node."""

        allowed = {EdgeType(item) for item in edge_types} if edge_types else None
        edge_pool = []
        if direction in {"out", "both"}:
            edge_pool.extend(self._outgoing.get(node_id, []))
        if direction in {"in", "both"}:
            edge_pool.extend(self._incoming.get(node_id, []))
        results: list[tuple[Edge, Node]] = []
        for edge in edge_pool:
            if allowed and edge.edge_type not in allowed:
                continue
            adjacent_id = edge.target_id if edge.source_id == node_id else edge.source_id
            results.append((edge, self.nodes[adjacent_id]))
        return results

    def shortest_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 4,
        edge_types: Iterable[EdgeType | str] | None = None,
    ) -> list[str]:
        """Find a shortest undirected path between two graph nodes."""

        if start_id not in self.nodes or end_id not in self.nodes:
            return []
        queue: deque[tuple[str, list[str]]] = deque([(start_id, [start_id])])
        visited = {start_id}
        while queue:
            node_id, path = queue.popleft()
            if node_id == end_id:
                return path
            if len(path) > max_depth:
                continue
            for _, neighbor in self.neighbors(node_id, edge_types=edge_types, direction="both"):
                if neighbor.id in visited:
                    continue
                visited.add(neighbor.id)
                queue.append((neighbor.id, [*path, neighbor.id]))
        return []
