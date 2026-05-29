"""Small, polite arXiv API client for the first single-paper workflow.

The implementation intentionally uses only the Python standard library.  It can
fetch a paper by arXiv ID or URL and can query AI-related category feeds for the
next milestone without adding another dependency on day one.
"""

from __future__ import annotations

import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

from arxiv_copilot.models import PaperMetadata

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_ABS_URL = "https://arxiv.org/abs/{arxiv_id}"
ARXIV_PDF_URL = "https://arxiv.org/pdf/{arxiv_id}.pdf"
AI_CATEGORIES = ("cs.AI", "cs.LG", "cs.CV", "cs.CL", "stat.ML", "eess.AS")
ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}
ARXIV_ID_PATTERN = re.compile(
    r"(?P<id>(?:\d{4}\.\d{4,5})(?:v\d+)?|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)",
    re.IGNORECASE,
)


class ArxivClientError(RuntimeError):
    """Raised when arXiv returns malformed data or a request cannot be fulfilled."""


@dataclass(slots=True)
class ArxivClient:
    """Client for querying and normalizing arXiv Atom API responses."""

    base_url: str = ARXIV_API_URL
    user_agent: str = "arxiv-research-copilot/0.1 (mailto:research@example.com)"
    polite_delay_seconds: float = 3.0
    timeout_seconds: float = 20.0
    _last_request_at: float = field(default=0.0, init=False, repr=False)

    def fetch_by_id(self, arxiv_id: str) -> PaperMetadata:
        """Fetch one paper by arXiv ID and return normalized metadata."""

        entries = self.query(id_list=[normalize_arxiv_id(arxiv_id)], max_results=1)
        if not entries:
            raise ArxivClientError(f"No arXiv paper found for ID: {arxiv_id}")
        return entries[0]

    def fetch_by_url(self, url: str) -> PaperMetadata:
        """Extract an arXiv ID from a URL, then fetch normalized metadata."""

        return self.fetch_by_id(extract_arxiv_id(url))

    def query_category(
        self,
        category: str,
        *,
        start: int = 0,
        max_results: int = 10,
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
    ) -> list[PaperMetadata]:
        """Query one arXiv category feed, such as ``cs.AI`` or ``cs.LG``."""

        return self.query(
            search_query=f"cat:{category}",
            start=start,
            max_results=max_results,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def detect_new_ai_papers(
        self,
        *,
        known_arxiv_ids: Iterable[str] = (),
        categories: Iterable[str] = AI_CATEGORIES,
        max_results_per_category: int = 5,
    ) -> list[PaperMetadata]:
        """Return recent AI-family papers whose arXiv IDs are not already known."""

        known = {normalize_arxiv_id(arxiv_id) for arxiv_id in known_arxiv_ids}
        papers_by_id: dict[str, PaperMetadata] = {}
        for category in categories:
            for paper in self.query_category(
                category, max_results=max_results_per_category
            ):
                if paper.arxiv_id not in known:
                    papers_by_id.setdefault(paper.arxiv_id, paper)
        return sorted(
            papers_by_id.values(), key=lambda paper: paper.published_at, reverse=True
        )

    def query(
        self,
        *,
        search_query: str | None = None,
        id_list: Iterable[str] = (),
        start: int = 0,
        max_results: int = 10,
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
    ) -> list[PaperMetadata]:
        """Run an arXiv API query and normalize all returned entries."""

        params = {
            "start": str(start),
            "max_results": str(max_results),
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }
        ids = [normalize_arxiv_id(arxiv_id) for arxiv_id in id_list]
        if ids:
            params["id_list"] = ",".join(ids)
        if search_query:
            params["search_query"] = search_query
        if not ids and not search_query:
            raise ValueError("Provide either search_query or id_list.")

        root = self._get_atom(params)
        return [parse_entry(entry) for entry in root.findall("atom:entry", ATOM_NS)]

    def _get_atom(self, params: dict[str, str]) -> ET.Element:
        """Perform a polite arXiv request and parse the Atom response."""

        elapsed = time.monotonic() - self._last_request_at
        if self._last_request_at and elapsed < self.polite_delay_seconds:
            time.sleep(self.polite_delay_seconds - elapsed)

        url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urllib.request.urlopen(
                request, timeout=self.timeout_seconds
            ) as response:
                body = response.read()
        except OSError as exc:
            raise ArxivClientError(f"arXiv request failed: {exc}") from exc
        finally:
            self._last_request_at = time.monotonic()

        try:
            return ET.fromstring(body)
        except ET.ParseError as exc:
            raise ArxivClientError("arXiv returned invalid Atom XML.") from exc


def extract_arxiv_id(value: str) -> str:
    """Extract and normalize an arXiv ID from an ID, abstract URL, or PDF URL."""

    value = value.strip()
    if not value:
        raise ValueError("arXiv ID or URL cannot be empty.")

    parsed = urllib.parse.urlparse(value)
    candidate = value
    if parsed.netloc:
        path_parts = [part for part in parsed.path.split("/") if part]
        if path_parts and path_parts[0] in {"abs", "pdf"} and len(path_parts) >= 2:
            candidate = path_parts[1].removesuffix(".pdf")

    match = ARXIV_ID_PATTERN.search(candidate)
    if not match:
        raise ValueError(f"Could not extract an arXiv ID from: {value}")
    return normalize_arxiv_id(match.group("id").removesuffix(".pdf"))


def normalize_arxiv_id(arxiv_id: str) -> str:
    """Normalize common arXiv ID inputs to the canonical API ID form."""

    arxiv_id = arxiv_id.strip()
    arxiv_id = arxiv_id.removeprefix("arXiv:")
    arxiv_id = arxiv_id.removesuffix(".pdf")
    if not ARXIV_ID_PATTERN.fullmatch(arxiv_id):
        raise ValueError(f"Invalid arXiv ID: {arxiv_id}")
    return arxiv_id


def parse_entry(entry: ET.Element) -> PaperMetadata:
    """Convert one Atom ``entry`` element into ``PaperMetadata``."""

    arxiv_url = _required_text(entry, "atom:id")
    arxiv_id = extract_arxiv_id(arxiv_url)
    categories = [
        category.attrib["term"]
        for category in entry.findall("atom:category", ATOM_NS)
        if "term" in category.attrib
    ]
    primary_category = _find_optional(entry, "arxiv:primary_category")
    primary_category_term = (
        primary_category.attrib.get("term")
        if primary_category is not None
        else (categories[0] if categories else "")
    )
    pdf_url = _find_pdf_url(entry) or ARXIV_PDF_URL.format(arxiv_id=arxiv_id)

    return PaperMetadata(
        arxiv_id=arxiv_id,
        title=_clean_text(_required_text(entry, "atom:title")),
        authors=[
            _clean_text(_required_text(author, "atom:name"))
            for author in entry.findall("atom:author", ATOM_NS)
        ],
        abstract=_clean_text(_required_text(entry, "atom:summary")),
        published_at=_parse_datetime(_required_text(entry, "atom:published")),
        updated_at=_parse_datetime(_required_text(entry, "atom:updated")),
        categories=categories,
        primary_category=primary_category_term,
        arxiv_url=arxiv_url,
        pdf_url=pdf_url,
        doi=_optional_text(entry, "arxiv:doi"),
        journal_ref=_optional_text(entry, "arxiv:journal_ref"),
        comment=_optional_text(entry, "arxiv:comment"),
    )


def _find_pdf_url(entry: ET.Element) -> str | None:
    for link in entry.findall("atom:link", ATOM_NS):
        if (
            link.attrib.get("title") == "pdf"
            or link.attrib.get("type") == "application/pdf"
        ):
            return link.attrib.get("href")
    return None


def _find_optional(entry: ET.Element, path: str) -> ET.Element | None:
    return entry.find(path, ATOM_NS)


def _optional_text(entry: ET.Element, path: str) -> str | None:
    node = _find_optional(entry, path)
    if node is None or node.text is None:
        return None
    return _clean_text(node.text)


def _required_text(entry: ET.Element, path: str) -> str:
    value = _optional_text(entry, path)
    if value is None:
        raise ArxivClientError(f"arXiv entry is missing required field: {path}")
    return value


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
