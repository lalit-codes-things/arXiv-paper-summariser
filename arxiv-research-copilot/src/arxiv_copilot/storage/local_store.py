"""Local JSON persistence for processing results."""

from __future__ import annotations

from pathlib import Path

from arxiv_copilot.config import Settings
from arxiv_copilot.models import ProcessingResult


class LocalStore:
    """Persist pipeline outputs as structured JSON files."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def save_summary(self, result: ProcessingResult) -> Path:
        """Save a processing result to the summaries directory."""
        output_path = self.settings.summaries_dir / f"{self._safe_filename(result.metadata.arxiv_id)}.json"
        output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        return output_path

    @staticmethod
    def _safe_filename(arxiv_id: str) -> str:
        return arxiv_id.replace("/", "_").replace(":", "_")
