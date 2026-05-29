"""Paper comparison engine entry points."""

from __future__ import annotations

from .agents import PaperComparisonAgent
from .models import ComparisonResult, Paper


class PaperComparisonEngine:
    """Compare methods, benchmarks, limitations, and compute costs for a paper set."""

    def __init__(self) -> None:
        self.agent = PaperComparisonAgent()

    def compare(self, papers: list[Paper]) -> ComparisonResult:
        """Return a structured comparison matrix."""

        return self.agent.compare(papers)
