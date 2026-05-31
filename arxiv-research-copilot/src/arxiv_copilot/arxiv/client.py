"""Client for fetching paper metadata from the arXiv API."""

from __future__ import annotations

from datetime import datetime
import re
import xml.etree.ElementTree as ET

import requests

from arxiv_copilot.config import Settings
from arxiv_copilot.models import PaperMetadata

ATOM_NS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"


class ArxivClient:
    """Small arXiv API client focused on exact paper lookup by arXiv ID."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def fetch_by_id(self, arxiv_id: str) -> PaperMetadata:
        """Fetch and parse metadata for a single arXiv paper ID."""
        normalized_id = self._normalize_arxiv_id(arxiv_id)
        response = requests.get(
            self.settings.arxiv_api_base_url,
            params={"id_list": normalized_id},
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        return self._parse_metadata(response.text, normalized_id)

    def _parse_metadata(self, xml_payload: str, requested_id: str) -> PaperMetadata:
        root = ET.fromstring(xml_payload)
        entry = root.find(f"{ATOM_NS}entry")
        if entry is None:
            raise ValueError(f"No arXiv paper found for ID: {requested_id}")

        title = self._clean_text(self._required_child_text(entry, "title"))
        abstract = self._clean_text(self._required_child_text(entry, "summary"))
        published = datetime.fromisoformat(self._required_child_text(entry, "published").replace("Z", "+00:00"))
        arxiv_id = self._extract_arxiv_id(self._required_child_text(entry, "id"))
        authors = [self._clean_text(author.findtext(f"{ATOM_NS}name", default="")) for author in entry.findall(f"{ATOM_NS}author")]
        categories = [category.attrib["term"] for category in entry.findall(f"{ATOM_NS}category") if "term" in category.attrib]
        pdf_url = self._extract_pdf_url(entry, arxiv_id)

        return PaperMetadata(
            title=title,
            authors=[author for author in authors if author],
            abstract=abstract,
            arxiv_id=arxiv_id,
            pdf_url=pdf_url,
            published=published,
            categories=categories,
        )

    @staticmethod
    def _normalize_arxiv_id(arxiv_id: str) -> str:
        stripped = arxiv_id.strip()
        stripped = stripped.removeprefix("https://arxiv.org/abs/").removeprefix("http://arxiv.org/abs/")
        return stripped

    @staticmethod
    def _extract_arxiv_id(entry_id_url: str) -> str:
        return entry_id_url.rstrip("/").split("/")[-1]

    @staticmethod
    def _extract_pdf_url(entry: ET.Element, arxiv_id: str) -> str:
        for link in entry.findall(f"{ATOM_NS}link"):
            if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                href = link.attrib.get("href")
                if href:
                    return href
        return f"https://arxiv.org/pdf/{arxiv_id}"

    @staticmethod
    def _required_child_text(entry: ET.Element, child_name: str) -> str:
        value = entry.findtext(f"{ATOM_NS}{child_name}")
        if value is None:
            raise ValueError(f"arXiv response missing required field: {child_name}")
        return value

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
