"""Fetch and ingest papers from the arXiv API into the V3 database."""
from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime

import httpx

from app.repositories.papers import PaperRepository
from app.schemas.paper import PaperCreate

ARXIV_API = "https://export.arxiv.org/api/query"
ATOM_NS = "{http://www.w3.org/2005/Atom}"


class ArxivIngestionService:
    """Fetch arXiv Atom records and persist them as V3 papers."""

    def __init__(self, papers: PaperRepository):
        self.papers = papers

    async def ingest_category(self, category: str = "cs.AI", max_results: int = 20) -> list[str]:
        """Fetch recent papers from arXiv and upsert them into the database."""
        params = {
            "search_query": f"cat:{category}",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": max_results,
        }
        text = await self._fetch(params)
        root = ET.fromstring(text)
        ingested: list[str] = []

        for entry in root.findall(f"{ATOM_NS}entry"):
            payload = self._entry_to_payload(entry, category=category)
            await self.papers.upsert(payload)
            ingested.append(payload.id or payload.arxiv_id)

        return ingested

    async def ingest_by_id(self, arxiv_id: str) -> str:
        """Fetch a single paper by arXiv ID and upsert it."""
        text = await self._fetch({"id_list": arxiv_id, "max_results": 1})
        root = ET.fromstring(text)
        entry = root.find(f"{ATOM_NS}entry")
        if entry is None:
            raise ValueError(f"No paper found for arXiv ID: {arxiv_id}")

        payload = self._entry_to_payload(entry)
        await self.papers.upsert(payload)
        return payload.id or payload.arxiv_id

    async def _fetch(self, params: dict[str, object]) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(ARXIV_API, params=params)
            response.raise_for_status()
        return response.text

    def _entry_to_payload(self, entry: ET.Element, *, category: str | None = None) -> PaperCreate:
        arxiv_id = entry.findtext(f"{ATOM_NS}id", "").rsplit("/", 1)[-1].strip()
        title = " ".join((entry.findtext(f"{ATOM_NS}title") or "").split())
        abstract = " ".join((entry.findtext(f"{ATOM_NS}summary") or "").split())
        authors = [a.findtext(f"{ATOM_NS}name") or "" for a in entry.findall(f"{ATOM_NS}author")]
        published_str = entry.findtext(f"{ATOM_NS}published") or ""
        updated_str = entry.findtext(f"{ATOM_NS}updated") or published_str
        published_at = self._parse_datetime(published_str)
        updated_at = self._parse_datetime(updated_str)
        categories = [
            c.attrib.get("term", "")
            for c in entry.findall(f"{ATOM_NS}category")
            if c.attrib.get("term")
        ]

        paper_id = hashlib.md5(arxiv_id.encode(), usedforsecurity=False).hexdigest()[:16]
        metadata = {"source": "arxiv"}
        if category:
            metadata["category"] = category
        return PaperCreate(
            id=paper_id,
            arxiv_id=arxiv_id,
            title=title,
            abstract=abstract,
            authors=authors,
            topics=categories,
            contributions=[],
            methodology=None,
            published_at=published_at,
            updated_at=updated_at,
            metadata=metadata,
        )

    @staticmethod
    def _parse_datetime(value: str) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
