"""Shared data structures for multimodal paper understanding."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Modality(str, Enum):
    """Research-paper modalities understood by the V16 platform."""

    FIGURE = "figure"
    CHART = "chart"
    EQUATION = "equation"
    ARCHITECTURE_DIAGRAM = "architecture_diagram"
    TABLE = "table"
    VIDEO = "video"
    OCR = "ocr"


@dataclass(frozen=True)
class PaperAsset:
    """A detected asset extracted from a paper or its supplementary material."""

    asset_id: str
    modality: Modality
    source: str
    page: int | None = None
    bbox: tuple[float, float, float, float] | None = None
    caption: str = ""
    content: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UnderstandingResult:
    """Normalized output from a modality-specific parser or reasoning workflow."""

    asset_id: str
    modality: Modality
    summary: str
    evidence: list[str] = field(default_factory=list)
    extracted: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Render the result as a concise human-readable Markdown block."""

        lines = [f"### {self.modality.value}: {self.asset_id}", self.summary]
        if self.evidence:
            lines.append("**Evidence**")
            lines.extend(f"- {item}" for item in self.evidence)
        if self.warnings:
            lines.append("**Warnings**")
            lines.extend(f"- {item}" for item in self.warnings)
        return "\n".join(lines)
