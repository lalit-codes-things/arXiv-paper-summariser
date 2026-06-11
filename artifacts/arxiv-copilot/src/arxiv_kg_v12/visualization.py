"""Graph visualization engine for V12."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

from .graph import KnowledgeGraph
from .schema import EdgeType, NodeType


NODE_COLORS = {
    NodeType.PAPER: "#2563eb",
    NodeType.AUTHOR: "#16a34a",
    NodeType.DATASET: "#f97316",
    NodeType.MODEL: "#9333ea",
    NodeType.METHOD: "#0891b2",
    NodeType.CONFERENCE: "#64748b",
    NodeType.BENCHMARK: "#dc2626",
}


class GraphVisualizationEngine:
    """Export interactive and static graph visualization assets."""

    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph

    def to_cytoscape(self) -> dict[str, list[dict[str, Any]]]:
        """Return Cytoscape.js-compatible node and edge elements."""

        nodes = [
            {
                "data": {
                    "id": node.id,
                    "label": node.properties.get("title") or node.properties.get("name") or node.id,
                    "type": node.node_type.value,
                    "color": NODE_COLORS[node.node_type],
                    **node.properties,
                }
            }
            for node in self.graph.nodes.values()
        ]
        edges = [
            {
                "data": {
                    "id": f"{edge.source_id}->{edge.target_id}:{edge.edge_type.value}:{index}",
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "label": edge.edge_type.value.lower(),
                    "type": edge.edge_type.value,
                    **edge.properties,
                }
            }
            for index, edge in enumerate(self.graph.edges)
        ]
        return {"nodes": nodes, "edges": edges}

    def to_mermaid(self) -> str:
        """Render a Mermaid flowchart for docs, notebooks, and markdown previews."""

        lines = ["flowchart LR"]
        for node in self.graph.nodes.values():
            label = escape(str(node.properties.get("title") or node.properties.get("name") or node.id))
            lines.append(f'  {self._safe_id(node.id)}["{label}<br/>{node.node_type.value}"]')
        for edge in self.graph.edges:
            lines.append(
                f"  {self._safe_id(edge.source_id)} -- {edge.edge_type.value.lower()} --> {self._safe_id(edge.target_id)}"
            )
        return "\n".join(lines)

    def write_html(self, path: str | Path, title: str = "V12 AI Research Knowledge Graph") -> Path:
        """Write a standalone interactive Cytoscape.js visualization page."""

        output_path = Path(path)
        elements = self.to_cytoscape()
        html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{escape(title)}</title>
  <script src=\"https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js\"></script>
  <style>
    body {{ margin: 0; font-family: Inter, system-ui, sans-serif; background: #0f172a; color: #e2e8f0; }}
    header {{ padding: 1rem 1.25rem; border-bottom: 1px solid #334155; }}
    #graph {{ width: 100vw; height: calc(100vh - 74px); }}
  </style>
</head>
<body>
  <header><strong>{escape(title)}</strong> · {len(self.graph.nodes)} nodes · {len(self.graph.edges)} edges</header>
  <div id=\"graph\"></div>
  <script>
    const elements = {json.dumps(elements)};
    cytoscape({{
      container: document.getElementById('graph'),
      elements: [...elements.nodes, ...elements.edges],
      style: [
        {{ selector: 'node', style: {{ 'label': 'data(label)', 'background-color': 'data(color)', 'color': '#e2e8f0', 'text-outline-color': '#0f172a', 'text-outline-width': 2, 'font-size': 10 }} }},
        {{ selector: 'edge', style: {{ 'label': 'data(label)', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'line-color': '#94a3b8', 'target-arrow-color': '#94a3b8', 'font-size': 8, 'color': '#cbd5e1' }} }}
      ],
      layout: {{ name: 'cose', animate: false }}
    }});
  </script>
</body>
</html>
"""
        output_path.write_text(html, encoding="utf-8")
        return output_path

    def _safe_id(self, node_id: str) -> str:
        return "n" + "".join(char if char.isalnum() else "_" for char in node_id)
