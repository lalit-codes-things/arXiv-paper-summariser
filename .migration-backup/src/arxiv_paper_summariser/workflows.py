"""Review generation workflows for V8."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .engine import LiteratureSynthesisEngine
from .models import Paper, Review, ReviewConfig


class ReviewGenerationWorkflow:
    """Load paper collections, run synthesis, and export review artifacts."""

    def __init__(self, engine: LiteratureSynthesisEngine | None = None) -> None:
        self.engine = engine or LiteratureSynthesisEngine()

    def from_records(self, records: list[dict[str, Any]], config: ReviewConfig | None = None) -> Review:
        """Generate a review from dictionaries, such as JSON or CSV rows."""

        papers = [self._paper_from_record(record) for record in records]
        engine = LiteratureSynthesisEngine(config) if config else self.engine
        return engine.generate_review(papers)

    def from_json(self, path: str | Path, config: ReviewConfig | None = None) -> Review:
        """Generate a review from a JSON file containing a list of papers."""

        records = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError("Paper JSON must contain a list of paper records.")
        return self.from_records(records, config=config)

    def export_markdown(self, review: Review, path: str | Path) -> Path:
        """Write a generated review to Markdown."""

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(review.to_markdown(), encoding="utf-8")
        return output_path

    @staticmethod
    def _paper_from_record(record: dict[str, Any]) -> Paper:
        required = {"id", "title", "authors", "year", "abstract"}
        missing = sorted(required - record.keys())
        if missing:
            raise ValueError(f"Missing required paper fields: {', '.join(missing)}")
        return Paper(
            id=str(record["id"]),
            title=str(record["title"]),
            authors=tuple(record.get("authors") or ()),
            year=int(record["year"]),
            abstract=str(record["abstract"]),
            summary=str(record.get("summary", "")),
            keywords=tuple(record.get("keywords", ()) or ()),
            citations=tuple(record.get("citations", ()) or ()),
            venue=str(record.get("venue", "")),
            doi=str(record.get("doi", "")),
            url=str(record.get("url", "")),
            claims=tuple(record.get("claims", ()) or ()),
            methods=tuple(record.get("methods", ()) or ()),
            findings=tuple(record.get("findings", ()) or ()),
            limitations=tuple(record.get("limitations", ()) or ()),
            metadata=dict(record.get("metadata", {}) or {}),
        )
