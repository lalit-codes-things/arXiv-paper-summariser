"""Architecture diagram parsing and system-graph analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .modalities import Modality, PaperAsset, UnderstandingResult
from .ocr import OCRPipeline


@dataclass
class ArchitectureDiagramParser:
    """Converts architecture diagrams into components, edges, and data-flow notes."""

    ocr: OCRPipeline

    def parse(self, asset: PaperAsset) -> UnderstandingResult:
        graph = self._extract_graph(asset)
        ocr_result = self.ocr.run(asset)
        labels = graph.get("labels") or ocr_result.extracted.get("tokens", {}).get("variables", [])
        components = graph.get("components", labels)
        edges = graph.get("edges", [])
        flow = self._describe_flow(components, edges)

        return UnderstandingResult(
            asset_id=asset.asset_id,
            modality=Modality.ARCHITECTURE_DIAGRAM,
            summary=(
                f"Parsed architecture diagram with {len(components)} component(s) "
                f"and {len(edges)} directed connection(s)."
            ),
            evidence=flow,
            extracted={"components": components, "edges": edges, "labels": labels, "ocr": ocr_result.extracted},
            confidence=0.88 if components or edges else 0.25,
            warnings=[] if components or edges else ["No explicit diagram graph metadata was found; OCR labels were used as fallback."],
        )

    @staticmethod
    def _extract_graph(asset: PaperAsset) -> dict[str, Any]:
        graph = asset.metadata.get("graph", {})
        return graph if isinstance(graph, dict) else {}

    @staticmethod
    def _describe_flow(components: list[Any], edges: list[Any]) -> list[str]:
        if not edges:
            return [f"Detected component `{component}`." for component in components]
        descriptions = []
        for edge in edges:
            if isinstance(edge, dict):
                source = edge.get("source", "unknown")
                target = edge.get("target", "unknown")
                label = edge.get("label")
            elif isinstance(edge, (tuple, list)) and len(edge) >= 2:
                source, target = edge[0], edge[1]
                label = edge[2] if len(edge) > 2 else None
            else:
                descriptions.append(f"Detected connection `{edge}`.")
                continue
            suffix = f" carrying `{label}`" if label else ""
            descriptions.append(f"Data/control flows from `{source}` to `{target}`{suffix}.")
        return descriptions
