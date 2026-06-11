"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the Arxiv Research Copilot pipeline."""

    openai_api_key: str
    openai_base_url: str
    openai_model: str
    notion_token: str | None
    notion_database_id: str | None
    arxiv_api_base_url: str
    app_data_dir: Path
    request_timeout_seconds: int
    max_paper_text_chars: int

    @property
    def raw_pdf_dir(self) -> Path:
        """Directory where downloaded PDFs are stored."""
        return self.app_data_dir / "raw_pdfs"

    @property
    def extracted_dir(self) -> Path:
        """Directory where extracted text artifacts are stored."""
        return self.app_data_dir / "extracted"

    @property
    def summaries_dir(self) -> Path:
        """Directory where structured summary JSON files are stored."""
        return self.app_data_dir / "summaries"

    @property
    def notion_enabled(self) -> bool:
        """Return whether the process has enough configuration to sync to Notion."""
        return bool(self.notion_token and self.notion_database_id)

    def ensure_data_directories(self) -> None:
        """Create all local data directories required by the pipeline."""
        self.raw_pdf_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)


def _read_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


def get_settings() -> Settings:
    """Build application settings from environment variables."""
    settings = Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        notion_token=os.getenv("NOTION_TOKEN"),
        notion_database_id=os.getenv("NOTION_DATABASE_ID"),
        arxiv_api_base_url=os.getenv("ARXIV_API_BASE_URL", "https://export.arxiv.org/api/query"),
        app_data_dir=Path(os.getenv("APP_DATA_DIR", "data")),
        request_timeout_seconds=_read_int("REQUEST_TIMEOUT_SECONDS", 30),
        max_paper_text_chars=_read_int("MAX_PAPER_TEXT_CHARS", 120_000),
    )
    settings.ensure_data_directories()
    return settings
