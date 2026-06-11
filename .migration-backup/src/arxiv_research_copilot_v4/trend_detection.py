"""Cohort-level trend detection for autonomous research monitoring."""

from __future__ import annotations

from collections import defaultdict

from .models import Paper, Trend
from .text import keyphrases


class TrendDetector:
    """Detect emerging topics, architectures, and frequently mentioned methods."""

    architecture_terms = {"transformer", "diffusion", "mamba", "moe", "retrieval", "agent", "graph", "vision language"}

    def detect(self, papers: list[Paper], *, limit: int = 10) -> list[Trend]:
        """Return ranked trends with evidence paper IDs."""

        phrase_to_papers: defaultdict[str, set[str]] = defaultdict(set)
        phrase_counts: defaultdict[str, int] = defaultdict(int)
        for paper in papers:
            for phrase, count in keyphrases(paper.title + " " + paper.abstract, limit=20):
                phrase_to_papers[phrase].add(paper.paper_id)
                phrase_counts[phrase] += count
        trends: list[Trend] = []
        for phrase, count in phrase_counts.items():
            support = len(phrase_to_papers[phrase])
            if support < 2 and count < 3:
                continue
            category = "architecture" if any(term in phrase for term in self.architecture_terms) else "topic"
            score = round((support * 4.0) + count + (3.0 if category == "architecture" else 0.0), 2)
            trends.append(Trend(phrase, score, sorted(phrase_to_papers[phrase]), category, f"Appears {count} times across {support} monitored papers."))
        return sorted(trends, key=lambda trend: trend.score, reverse=True)[:limit]
