"""PDF download and text extraction."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from arxiv_copilot.utils.http import HttpClient

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class PDFService:
    download_dir: Path = Path("data/pdfs")
    http: HttpClient = field(default_factory=HttpClient)

    def download(self, pdf_url: str, arxiv_id: str) -> Path:
        self.download_dir.mkdir(parents=True, exist_ok=True)
        path = self.download_dir / f"{_safe_name(arxiv_id)}.pdf"
        LOGGER.info("Downloading PDF %s to %s", pdf_url, path)
        path.write_bytes(self.http.get_bytes(pdf_url))
        return path

    def extract_text(self, path: Path) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Install arxiv-research-copilot[pdf] to extract PDF text") from exc

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(page.strip() for page in pages if page.strip())


def _safe_name(value: str) -> str:
    return value.replace("/", "_").replace(":", "_")
