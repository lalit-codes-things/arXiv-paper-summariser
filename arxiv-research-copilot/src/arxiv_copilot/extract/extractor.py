"""Text extraction from PDF files using PyMuPDF."""

from __future__ import annotations

from pathlib import Path

import fitz

from arxiv_copilot.config import Settings


class PdfTextExtractor:
    """Extract text from all pages of a PDF and persist the extracted text."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def extract(self, pdf_path: Path, arxiv_id: str) -> str:
        """Extract text from every page in a PDF."""
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF does not exist: {pdf_path}")

        page_texts: list[str] = []
        with fitz.open(pdf_path) as document:
            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text").strip()
                if text:
                    page_texts.append(f"\n\n--- Page {page_number} ---\n{text}")

        extracted_text = "".join(page_texts).strip()
        if not extracted_text:
            raise ValueError(f"No text could be extracted from PDF: {pdf_path}")

        output_path = self.settings.extracted_dir / f"{self._safe_filename(arxiv_id)}.txt"
        output_path.write_text(extracted_text, encoding="utf-8")
        return extracted_text

    @staticmethod
    def _safe_filename(arxiv_id: str) -> str:
        return arxiv_id.replace("/", "_").replace(":", "_")
