"""Semantic Scholar enrichment client."""

from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass, field

from arxiv_copilot.schemas import SemanticScholarPaper
from arxiv_copilot.utils.http import HttpClient

LOGGER = logging.getLogger(__name__)
DEFAULT_FIELDS = "paperId,title,url,citationCount,influentialCitationCount,authors,externalIds"


@dataclass(slots=True)
class SemanticScholarClient:
    http: HttpClient = field(default_factory=HttpClient)
    api_key: str | None = None
    base_url: str = "https://api.semanticscholar.org/graph/v1"

    def enrich_arxiv_id(self, arxiv_id: str) -> SemanticScholarPaper | None:
        headers = {"x-api-key": self.api_key} if self.api_key else None
        encoded_id = urllib.parse.quote(f"ARXIV:{arxiv_id}", safe=":")
        fields = urllib.parse.quote(DEFAULT_FIELDS)
        url = f"{self.base_url}/paper/{encoded_id}?fields={fields}"
        try:
            paper = self.http.get_json(url, headers=headers)
        except Exception as exc:  # noqa: BLE001 - enrichment must not break the pipeline.
            LOGGER.warning("Semantic Scholar lookup failed for %s: %s", arxiv_id, exc)
            return None

        result = SemanticScholarPaper(
            paper_id=paper.get("paperId"),
            title=paper.get("title"),
            url=paper.get("url"),
            citation_count=paper.get("citationCount"),
            influential_citation_count=paper.get("influentialCitationCount"),
            authors=paper.get("authors") or [],
        )
        if result.paper_id:
            try:
                result.influential_citations = self.influential_citations(result.paper_id)
            except Exception as exc:  # noqa: BLE001 - partial enrichment is acceptable.
                LOGGER.warning("Semantic Scholar citation enrichment failed for %s: %s", arxiv_id, exc)
            try:
                result.related_papers = self.related_papers(result.paper_id)
            except Exception as exc:  # noqa: BLE001 - partial enrichment is acceptable.
                LOGGER.warning("Semantic Scholar recommendation enrichment failed for %s: %s", arxiv_id, exc)
        return result

    def influential_citations(self, paper_id: str, *, limit: int = 10) -> list[dict]:
        fields = urllib.parse.quote("title,url,citationCount,influentialCitationCount,authors,year")
        url = f"{self.base_url}/paper/{paper_id}/citations?fields={fields}&limit={limit}"
        data = self.http.get_json(url, headers={"x-api-key": self.api_key} if self.api_key else None)
        items = [item.get("citingPaper", {}) for item in data.get("data", [])]
        return sorted(items, key=lambda item: item.get("influentialCitationCount") or 0, reverse=True)

    def related_papers(self, paper_id: str, *, limit: int = 10) -> list[dict]:
        fields = urllib.parse.quote("title,url,citationCount,authors,year,externalIds")
        url = f"{self.base_url}/paper/{paper_id}/recommendations?fields={fields}&limit={limit}"
        data = self.http.get_json(url, headers={"x-api-key": self.api_key} if self.api_key else None)
        return data.get("recommendedPapers", [])[:limit]
