"""Multimodal parsers for figures, charts, tables, and video supplements."""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Any, Iterable

from .modalities import Modality, PaperAsset, UnderstandingResult
from .ocr import OCRPipeline


@dataclass
class FigureUnderstandingParser:
    """Explains scientific figures using captions, OCR text, and detected visual entities."""

    ocr: OCRPipeline

    def parse(self, asset: PaperAsset) -> UnderstandingResult:
        ocr_result = self.ocr.run(asset)
        entities = list(asset.metadata.get("entities", []))
        caption = asset.caption or asset.metadata.get("caption", "")
        evidence = [item for item in (caption, ocr_result.extracted.get("text", "")) if item]
        evidence.extend(f"Detected visual entity: {entity}" for entity in entities)
        summary = self._summarize(caption, entities, ocr_result.extracted.get("text", ""))
        return UnderstandingResult(
            asset_id=asset.asset_id,
            modality=Modality.FIGURE,
            summary=summary,
            evidence=evidence,
            extracted={"caption": caption, "entities": entities, "ocr": ocr_result.extracted},
            confidence=0.84 if evidence else 0.2,
            warnings=[] if evidence else ["Figure lacks caption, OCR text, and detected entities."],
        )

    @staticmethod
    def _summarize(caption: str, entities: list[Any], ocr_text: str) -> str:
        anchors = []
        if caption:
            anchors.append("caption")
        if entities:
            anchors.append(f"{len(entities)} visual entity/entities")
        if ocr_text:
            anchors.append("embedded text")
        return "Figure understanding used " + ", ".join(anchors) + "." if anchors else "No figure content was available."


@dataclass
class ChartReasoningParser:
    """Performs lightweight chart reasoning from extracted series metadata."""

    ocr: OCRPipeline

    def parse(self, asset: PaperAsset) -> UnderstandingResult:
        chart = asset.metadata.get("chart", {}) if isinstance(asset.metadata.get("chart", {}), dict) else {}
        series = chart.get("series", [])
        insights = self._derive_insights(series)
        ocr_result = self.ocr.run(asset)
        axes = chart.get("axes", {})
        return UnderstandingResult(
            asset_id=asset.asset_id,
            modality=Modality.CHART,
            summary=(insights[0] if insights else "Chart parsed without enough numeric series data for trend reasoning."),
            evidence=insights + ([f"Axes: {axes}"] if axes else []),
            extracted={"chart": chart, "ocr": ocr_result.extracted},
            confidence=0.87 if insights else 0.35,
            warnings=[] if insights else ["Provide extracted chart series for richer reasoning."],
        )

    @staticmethod
    def _derive_insights(series: Iterable[dict[str, Any]]) -> list[str]:
        insights: list[str] = []
        for item in series:
            name = item.get("name", "series")
            values = [float(value) for value in item.get("values", []) if isinstance(value, (int, float))]
            if len(values) < 2:
                continue
            delta = values[-1] - values[0]
            direction = "increases" if delta > 0 else "decreases" if delta < 0 else "stays flat"
            insights.append(
                f"Series `{name}` {direction} from {values[0]:g} to {values[-1]:g}; "
                f"mean={statistics.fmean(values):g}, min={min(values):g}, max={max(values):g}."
            )
        return insights


@dataclass
class TableExtractionParser:
    """Extracts table schema, rows, and cell-level facts."""

    ocr: OCRPipeline

    def parse(self, asset: PaperAsset) -> UnderstandingResult:
        table = asset.metadata.get("table", {}) if isinstance(asset.metadata.get("table", {}), dict) else {}
        headers = list(table.get("headers", []))
        rows = list(table.get("rows", []))
        facts = self._facts(headers, rows)
        ocr_result = self.ocr.run(asset)
        return UnderstandingResult(
            asset_id=asset.asset_id,
            modality=Modality.TABLE,
            summary=f"Extracted table with {len(headers)} column(s) and {len(rows)} row(s).",
            evidence=facts[:8],
            extracted={"headers": headers, "rows": rows, "facts": facts, "ocr": ocr_result.extracted},
            confidence=0.9 if headers and rows else 0.3,
            warnings=[] if headers and rows else ["Structured table metadata was incomplete; OCR text is available as fallback."],
        )

    @staticmethod
    def _facts(headers: list[Any], rows: list[Any]) -> list[str]:
        facts: list[str] = []
        for row_index, row in enumerate(rows, start=1):
            if isinstance(row, dict):
                facts.extend(f"Row {row_index}: {key} = {value}" for key, value in row.items())
            elif isinstance(row, (list, tuple)):
                facts.extend(
                    f"Row {row_index}: {header} = {value}"
                    for header, value in zip(headers, row, strict=False)
                )
        return facts


@dataclass
class VideoUnderstandingParser:
    """Summarizes paper videos from transcripts, frame annotations, and temporal events."""

    ocr: OCRPipeline

    def parse(self, asset: PaperAsset) -> UnderstandingResult:
        transcript = asset.metadata.get("transcript", "")
        frames = list(asset.metadata.get("frames", []))
        events = list(asset.metadata.get("events", []))
        ocr_result = self.ocr.run(asset)
        evidence = []
        if transcript:
            evidence.append(f"Transcript: {transcript}")
        evidence.extend(f"Frame: {frame}" for frame in frames[:5])
        evidence.extend(f"Event: {event}" for event in events[:5])
        return UnderstandingResult(
            asset_id=asset.asset_id,
            modality=Modality.VIDEO,
            summary=f"Video understanding combined transcript, {len(frames)} frame annotation(s), and {len(events)} temporal event(s).",
            evidence=evidence,
            extracted={"transcript": transcript, "frames": frames, "events": events, "ocr": ocr_result.extracted},
            confidence=0.86 if evidence else 0.2,
            warnings=[] if evidence else ["Video has no transcript, frame annotations, or temporal events."],
        )
