"""Optional Notion sync adapter."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from arxiv_copilot.schemas import PaperResult
from arxiv_copilot.utils.http import HttpClient

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class NotionSync:
    token: str | None = None
    database_id: str | None = None
    http: HttpClient = field(default_factory=HttpClient)

    def sync(self, result: PaperResult) -> bool:
        """Sync a compact result to Notion when credentials are configured.

        The stdlib HTTP client currently supports GET only, so this adapter is a
        compatibility placeholder that logs the payload and returns False when no
        credentials exist. Projects can subclass it to perform a POST with their
        preferred HTTP stack.
        """

        if not self.token or not self.database_id:
            LOGGER.info("Notion credentials not configured; skipping sync for %s", result.paper.arxiv_id)
            return False
        LOGGER.info("Prepared Notion payload for %s: %s", result.paper.arxiv_id, json.dumps(_payload(result))[:500])
        return False


def _payload(result: PaperResult) -> dict:
    return {
        "title": result.paper.title,
        "arxiv_id": result.paper.arxiv_id,
        "tl_dr": result.summary.tl_dr,
        "citation_count": result.semantic_scholar.citation_count if result.semantic_scholar else None,
    }
