"""PDF download utilities for arXiv papers."""

from __future__ import annotations

from pathlib import Path

import requests

from arxiv_copilot.config import Settings
from arxiv_copilot.models import PaperMetadata


class PdfDownloader:
    """Download paper PDFs to the local raw PDF store."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def download(self, metadata: PaperMetadata) -> Path:
        """Download a paper PDF and return its local path."""
        target_path = self.settings.raw_pdf_dir / f"{self._safe_filename(metadata.arxiv_id)}.pdf"
        response = requests.get(str(metadata.pdf_url), timeout=self.settings.request_timeout_seconds)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "pdf" not in content_type.lower() and not response.content.startswith(b"%PDF"):
            raise ValueError(f"Downloaded content for {metadata.arxiv_id} does not look like a PDF")
        target_path.write_bytes(response.content)
        return target_path

    @staticmethod
    def _safe_filename(arxiv_id: str) -> str:
        return arxiv_id.replace("/", "_").replace(":", "_")
