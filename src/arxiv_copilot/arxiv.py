"""arXiv API client and feed helpers."""

from __future__ import annotations

import logging
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from arxiv_copilot.schemas import ArxivPaper
from arxiv_copilot.utils.http import HttpClient

LOGGER = logging.getLogger(__name__)
ATOM = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


@dataclass(slots=True)
class ArxivClient:
    http: HttpClient = field(default_factory=HttpClient)
    base_url: str = "https://export.arxiv.org/api/query"

    def fetch_by_id(self, arxiv_id: str) -> ArxivPaper:
        papers = self.search(f"id:{arxiv_id}", max_results=1)
        if not papers:
            raise LookupError(f"No arXiv paper found for {arxiv_id}")
        return papers[0]

    def newest(self, category: str = "cs.AI", *, max_results: int = 10) -> list[ArxivPaper]:
        return self.search(f"cat:{category}", max_results=max_results, sort_by="submittedDate", sort_order="descending")

    def search(self, query: str, *, max_results: int = 10, sort_by: str = "relevance", sort_order: str = "descending") -> list[ArxivPaper]:
        params = urllib.parse.urlencode(
            {
                "search_query": query,
                "start": 0,
                "max_results": max_results,
                "sortBy": sort_by,
                "sortOrder": sort_order,
            }
        )
        url = f"{self.base_url}?{params}"
        LOGGER.info("Fetching arXiv query: %s", query)
        return _parse_feed(self.http.get_text(url))


def _parse_feed(xml_text: str) -> list[ArxivPaper]:
    root = ET.fromstring(xml_text)
    papers: list[ArxivPaper] = []
    for entry in root.findall("atom:entry", ATOM):
        arxiv_id = _text(entry, "atom:id").rsplit("/", 1)[-1]
        pdf_url = None
        entry_url = None
        for link in entry.findall("atom:link", ATOM):
            href = link.attrib.get("href")
            if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                pdf_url = href
            elif link.attrib.get("rel") == "alternate":
                entry_url = href
        categories = [category.attrib.get("term", "") for category in entry.findall("atom:category", ATOM)]
        papers.append(
            ArxivPaper(
                arxiv_id=arxiv_id,
                title=" ".join(_text(entry, "atom:title").split()),
                abstract=" ".join(_text(entry, "atom:summary").split()),
                authors=[_text(author, "atom:name") for author in entry.findall("atom:author", ATOM)],
                published=_text(entry, "atom:published") or None,
                updated=_text(entry, "atom:updated") or None,
                pdf_url=pdf_url,
                entry_url=entry_url,
                categories=[category for category in categories if category],
            )
        )
    return papers


def _text(element: ET.Element, path: str) -> str:
    found = element.find(path, ATOM)
    return found.text.strip() if found is not None and found.text else ""
