"""Autonomous daily arXiv monitoring, summarization, ranking, and Notion export."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from .models import DailyDigest, Paper
from .orchestration import AgentOrchestrator, build_default_orchestrator
from .ranking import PaperRanker

ARXIV_NAMESPACE = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
DEFAULT_CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.CV", "stat.ML"]


class DigestSink(Protocol):
    """Destination for daily digest publishing."""

    def publish(self, digest: DailyDigest) -> None:
        """Publish a daily digest."""


class ArxivClient:
    """Small arXiv Atom API client for category monitoring."""

    endpoint = "https://export.arxiv.org/api/query"

    def fetch_recent(self, categories: list[str], *, max_results: int = 50) -> list[Paper]:
        """Fetch recent arXiv papers for the given categories."""

        query = " OR ".join(f"cat:{category}" for category in categories)
        params = urllib.parse.urlencode({"search_query": query, "sortBy": "submittedDate", "sortOrder": "descending", "max_results": max_results})
        with urllib.request.urlopen(f"{self.endpoint}?{params}", timeout=30) as response:
            payload = response.read()
        return self._parse(payload)

    def _parse(self, payload: bytes) -> list[Paper]:
        root = ET.fromstring(payload)
        papers: list[Paper] = []
        for entry in root.findall("atom:entry", ARXIV_NAMESPACE):
            paper_id = (entry.findtext("atom:id", default="", namespaces=ARXIV_NAMESPACE).rsplit("/", 1)[-1])
            title = " ".join(entry.findtext("atom:title", default="", namespaces=ARXIV_NAMESPACE).split())
            abstract = " ".join(entry.findtext("atom:summary", default="", namespaces=ARXIV_NAMESPACE).split())
            authors = [author.findtext("atom:name", default="", namespaces=ARXIV_NAMESPACE) for author in entry.findall("atom:author", ARXIV_NAMESPACE)]
            categories = [category.attrib.get("term", "") for category in entry.findall("atom:category", ARXIV_NAMESPACE)]
            published = datetime.fromisoformat(entry.findtext("atom:published", default=datetime.now(timezone.utc).isoformat(), namespaces=ARXIV_NAMESPACE).replace("Z", "+00:00"))
            updated = datetime.fromisoformat(entry.findtext("atom:updated", default=published.isoformat(), namespaces=ARXIV_NAMESPACE).replace("Z", "+00:00"))
            pdf_url = None
            for link in entry.findall("atom:link", ARXIV_NAMESPACE):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href")
            papers.append(Paper(paper_id, title, abstract, authors, categories, published, updated, entry.findtext("atom:id", default=None, namespaces=ARXIV_NAMESPACE), pdf_url, primary_category=categories[0] if categories else None))
        return papers


class JsonDigestSink:
    """Local sink that writes Notion-ready digest JSON."""

    def __init__(self, output_dir: str | Path = "digests") -> None:
        self.output_dir = Path(output_dir)

    def publish(self, digest: DailyDigest) -> None:
        """Persist a digest as JSON for automation or Notion import."""

        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{digest.date.date().isoformat()}-ai-research-digest.json"
        payload = asdict(digest)
        payload["date"] = digest.date.isoformat()
        path.write_text(json.dumps(payload, default=str, indent=2), encoding="utf-8")


class NotionDigestSink:
    """Notion push placeholder that can be wired to the Notion API by callers."""

    def __init__(self, database_id: str, token: str) -> None:
        self.database_id = database_id
        self.token = token

    def publish(self, digest: DailyDigest) -> None:
        """Raise a clear setup message until an integration-specific Notion client is supplied."""

        raise NotImplementedError("Configure a Notion API client to publish DailyDigest into database_id.")


class DailyMonitoringWorkflow:
    """Fetch, summarize, rank, graph, detect trends, and publish a daily AI digest."""

    def __init__(self, *, arxiv_client: ArxivClient | None = None, orchestrator: AgentOrchestrator | None = None, ranker: PaperRanker | None = None, sink: DigestSink | None = None) -> None:
        self.arxiv_client = arxiv_client or ArxivClient()
        self.orchestrator = orchestrator or build_default_orchestrator()
        self.ranker = ranker or PaperRanker()
        self.sink = sink or JsonDigestSink()

    def run(self, *, categories: list[str] | None = None, max_results: int = 50, top_n: int = 10) -> DailyDigest:
        """Execute daily monitoring for AI/ML arXiv categories."""

        categories = categories or DEFAULT_CATEGORIES
        papers = self.arxiv_client.fetch_recent(categories, max_results=max_results)
        workflow = self.orchestrator.run_research_workflow(papers)
        ranked = self.ranker.rank(papers, agent_results=workflow.agent_results)[:top_n]
        top_papers = [paper for paper, _ in ranked]
        summaries = {result.paper_id: result for result in workflow.agent_results if result.paper_id and result.agent.value == "summarizer"}
        digest = DailyDigest(datetime.now(timezone.utc), categories, top_papers, {paper.paper_id: score for paper, score in ranked}, workflow.trends, summaries, workflow.graph_stats)
        self.sink.publish(digest)
        return digest
