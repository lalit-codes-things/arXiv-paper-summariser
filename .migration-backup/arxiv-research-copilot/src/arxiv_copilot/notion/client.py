"""Notion client for syncing structured research notes."""

from __future__ import annotations

from notion_client import Client

from arxiv_copilot.config import Settings
from arxiv_copilot.models import ProcessingResult


class NotionResearchClient:
    """Create Notion pages for processed arXiv papers."""

    def __init__(self, settings: Settings) -> None:
        if not settings.notion_token or not settings.notion_database_id:
            raise ValueError("NOTION_TOKEN and NOTION_DATABASE_ID are required for Notion sync")
        self.database_id = settings.notion_database_id
        self.client = Client(auth=settings.notion_token)

    def create_paper_page(self, result: ProcessingResult) -> str:
        """Create a Notion database page and return the created page ID."""
        metadata = result.metadata
        summary = result.summary
        page = self.client.pages.create(
            parent={"database_id": self.database_id},
            properties={
                "Name": {"title": [{"text": {"content": metadata.title[:2000]}}]},
                "arXiv ID": {"rich_text": [{"text": {"content": metadata.arxiv_id}}]},
                "Published": {"date": {"start": metadata.published.date().isoformat()}},
                "PDF": {"url": str(metadata.pdf_url)},
            },
            children=self._build_children(result),
        )
        return str(page["id"])

    def _build_children(self, result: ProcessingResult) -> list[dict[str, object]]:
        metadata = result.metadata
        summary = result.summary
        return [
            self._heading("TL;DR"),
            self._paragraph(summary.tl_dr),
            self._heading("ELI5"),
            self._paragraph(summary.eli5),
            self._heading("Technical Summary"),
            self._paragraph(summary.technical_summary),
            self._heading("Key Contributions"),
            *[self._bulleted_item(item) for item in summary.key_contributions],
            self._heading("Limitations"),
            *[self._bulleted_item(item) for item in summary.limitations],
            self._heading("Future Work"),
            *[self._bulleted_item(item) for item in summary.future_work],
            self._heading("Metadata"),
            self._paragraph(f"Authors: {', '.join(metadata.authors)}"),
            self._paragraph(f"Categories: {', '.join(metadata.categories)}"),
            self._paragraph(f"Abstract: {metadata.abstract}"),
        ]

    @staticmethod
    def _heading(text: str) -> dict[str, object]:
        return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

    @staticmethod
    def _paragraph(text: str) -> dict[str, object]:
        return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]}}

    @staticmethod
    def _bulleted_item(text: str) -> dict[str, object]:
        return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]}}
