"""Importance ranking for autonomous paper monitoring."""

from __future__ import annotations

from collections import Counter
from math import exp

from .models import AgentResult, Paper
from .text import contains_any, keywords


class PaperRanker:
    """Rank papers with novelty, category, evaluation, citation, and trend signals."""

    high_signal_terms = {
        "state-of-the-art", "sota", "benchmark", "open-source", "dataset", "agent", "reasoning",
        "multimodal", "diffusion", "transformer", "retrieval", "rag", "alignment", "efficient",
    }
    target_categories = {"cs.AI", "cs.CL", "cs.LG", "cs.CV", "stat.ML"}

    def score(self, paper: Paper, *, cohort: list[Paper] | None = None, agent_results: list[AgentResult] | None = None) -> float:
        """Return a 0-100 importance score."""

        cohort = cohort or [paper]
        agent_results = agent_results or []
        text = f"{paper.title} {paper.abstract}"
        recency = 25.0 * exp(-paper.age_days / 14.0)
        category = 15.0 if self.target_categories.intersection(paper.categories) else 5.0
        evidence = 15.0 if contains_any(text, {"benchmark", "experiment", "outperform", "evaluation", "human eval"}) else 4.0
        reproducibility = 10.0 if contains_any(text, {"code", "github", "open-source", "dataset"}) else 2.0
        trend = self._trend_score(paper, cohort)
        agent_confidence = min(10.0, sum(result.confidence for result in agent_results if result.paper_id == paper.paper_id) * 1.2)
        return round(min(100.0, recency + category + evidence + reproducibility + trend + agent_confidence), 2)

    def rank(self, papers: list[Paper], *, agent_results: list[AgentResult] | None = None) -> list[tuple[Paper, float]]:
        """Return papers sorted by descending importance score."""

        return sorted(((paper, self.score(paper, cohort=papers, agent_results=agent_results)) for paper in papers), key=lambda item: item[1], reverse=True)

    def _trend_score(self, paper: Paper, cohort: list[Paper]) -> float:
        cohort_counts: Counter[str] = Counter()
        for candidate in cohort:
            cohort_counts.update(keywords(candidate.title + " " + candidate.abstract, limit=12))
        paper_words = set(keywords(paper.title + " " + paper.abstract, limit=12))
        repeated = sum(cohort_counts[word] for word in paper_words)
        high_signal = 8.0 if contains_any(paper.title + " " + paper.abstract, self.high_signal_terms) else 0.0
        return min(25.0, repeated * 1.5 + high_signal)
