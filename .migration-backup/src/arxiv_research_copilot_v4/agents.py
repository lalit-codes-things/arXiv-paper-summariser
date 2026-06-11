"""Autonomous research agents for summarization, analysis, comparison, and learning."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .models import AgentName, AgentResult, ComparisonResult, Paper, RoadmapStep
from .text import centroid_summary, contains_any, keywords, keyphrases, sentences


@dataclass(slots=True)
class AgentContext:
    """Context shared between agents during an orchestration run."""

    papers: list[Paper]
    previous_results: list[AgentResult]
    graph_memory: Any | None = None
    objective: str | None = None


class ResearchAgent(ABC):
    """Base interface for all V4 research agents."""

    name: AgentName

    @abstractmethod
    def run(self, paper: Paper, context: AgentContext) -> AgentResult:
        """Analyze a paper and return a structured result."""


class SummarizerAgent(ResearchAgent):
    """Produces Perplexity/NotebookLM-style concise paper summaries."""

    name = AgentName.SUMMARIZER

    def run(self, paper: Paper, context: AgentContext) -> AgentResult:
        core = centroid_summary(paper.abstract, max_sentences=3)
        topic_words = keywords(paper.title + " " + paper.abstract, limit=6)
        summary = f"{paper.title}: {core} Key topics: {', '.join(topic_words)}."
        return AgentResult(
            agent=self.name,
            paper_id=paper.paper_id,
            summary=summary,
            confidence=0.82,
            findings={"key_topics": topic_words, "tldr": core},
        )


class MethodologyAgent(ResearchAgent):
    """Extracts methods, datasets, benchmarks, and compute hints."""

    name = AgentName.METHODOLOGY
    method_markers = {"transformer", "diffusion", "rlhf", "retrieval", "rag", "graph", "agent", "benchmark", "dataset"}
    compute_markers = {"gpu", "tpu", "a100", "h100", "training", "parameters", "tokens", "compute"}

    def run(self, paper: Paper, context: AgentContext) -> AgentResult:
        phrases = [phrase for phrase, _ in keyphrases(paper.abstract, limit=8)]
        methods = [phrase for phrase in phrases if contains_any(phrase, self.method_markers)] or phrases[:4]
        compute_mentions = [sentence for sentence in sentences(paper.abstract) if contains_any(sentence, self.compute_markers)]
        summary = "Methods: " + (", ".join(methods) if methods else "not explicit in abstract")
        return AgentResult(
            agent=self.name,
            paper_id=paper.paper_id,
            summary=summary,
            confidence=0.74,
            findings={"methods": methods, "compute_mentions": compute_mentions, "benchmarks": self._benchmarks(paper)},
        )

    def _benchmarks(self, paper: Paper) -> list[str]:
        candidates = []
        for token in paper.abstract.replace("-", " ").split():
            stripped = token.strip(".,;:()[]")
            if stripped.isupper() and 2 <= len(stripped) <= 12:
                candidates.append(stripped)
        return sorted(set(candidates))[:10]


class CitationAgent(ResearchAgent):
    """Builds citation intelligence signals from metadata and graph memory."""

    name = AgentName.CITATION

    def run(self, paper: Paper, context: AgentContext) -> AgentResult:
        related = []
        if context.graph_memory is not None:
            related = context.graph_memory.related_papers(paper.paper_id, limit=5)
        author_network = defaultdict(list)
        for candidate in context.papers:
            for author in candidate.authors:
                author_network[author].append(candidate.paper_id)
        shared_author_papers = sorted({pid for author in paper.authors for pid in author_network[author] if pid != paper.paper_id})
        summary = f"Citation context: {len(related)} graph-related papers and {len(shared_author_papers)} shared-author papers detected."
        return AgentResult(
            agent=self.name,
            paper_id=paper.paper_id,
            summary=summary,
            confidence=0.70,
            findings={"related_papers": related, "shared_author_papers": shared_author_papers[:10]},
        )


class WeaknessDetectorAgent(ResearchAgent):
    """Flags likely limitations and missing evaluation evidence."""

    name = AgentName.WEAKNESS_DETECTOR
    limitation_markers = {"limitation", "limited", "future work", "assume", "synthetic", "small", "preliminary"}
    evaluation_markers = {"benchmark", "experiment", "evaluation", "outperform", "accuracy", "f1", "human"}

    def run(self, paper: Paper, context: AgentContext) -> AgentResult:
        limitation_sentences = [sentence for sentence in sentences(paper.abstract) if contains_any(sentence, self.limitation_markers)]
        has_eval = contains_any(paper.abstract, self.evaluation_markers)
        risks = limitation_sentences[:]
        if not has_eval:
            risks.append("Abstract does not clearly mention benchmarked empirical evaluation.")
        if not any(word in paper.abstract.lower() for word in ["code", "github", "open-source", "dataset"]):
            risks.append("Reproducibility artifacts are not visible in the abstract metadata.")
        summary = "Potential weaknesses: " + ("; ".join(risks) if risks else "no obvious abstract-level weaknesses detected")
        return AgentResult(self.name, paper.paper_id, summary, 0.68, {"risks": risks, "has_evaluation_signal": has_eval})


class TrendAnalysisAgent(ResearchAgent):
    """Detects local paper-level trend signals."""

    name = AgentName.TREND_ANALYSIS

    def run(self, paper: Paper, context: AgentContext) -> AgentResult:
        corpus = " ".join(candidate.title + " " + candidate.abstract for candidate in context.papers)
        global_phrases = dict(keyphrases(corpus, limit=50))
        paper_phrases = keyphrases(paper.title + " " + paper.abstract, limit=10)
        signals = [{"phrase": phrase, "cohort_frequency": global_phrases.get(phrase, count)} for phrase, count in paper_phrases[:6]]
        summary = "Trend signals: " + ", ".join(signal["phrase"] for signal in signals)
        return AgentResult(self.name, paper.paper_id, summary, 0.76, {"signals": signals})


class ResearchRoadmapAgent(ResearchAgent):
    """Creates learning roadmap hints from a paper."""

    name = AgentName.ROADMAP

    def run(self, paper: Paper, context: AgentContext) -> AgentResult:
        topic_words = keywords(paper.title + " " + paper.abstract, limit=5)
        steps = [
            RoadmapStep(1, "Foundations", f"Review prerequisites for {topic_words[0] if topic_words else paper.primary_category}.", [paper.paper_id], "One-page concept map"),
            RoadmapStep(2, "Core method", f"Reproduce the central method in {paper.title}.", [paper.paper_id], "Annotated implementation notes"),
            RoadmapStep(3, "Evaluation", "Compare reported benchmarks, limitations, and ablations.", [paper.paper_id], "Benchmark comparison table"),
        ]
        return AgentResult(self.name, paper.paper_id, "Roadmap generated with foundations, implementation, and evaluation steps.", 0.78, {"steps": [asdict(step) for step in steps]})


class PaperComparisonAgent(ResearchAgent):
    """Compares methods, benchmarks, limitations, and compute costs across papers."""

    name = AgentName.PAPER_COMPARISON

    def run(self, paper: Paper, context: AgentContext) -> AgentResult:
        peers = [candidate for candidate in context.papers if candidate.paper_id != paper.paper_id]
        overlaps = []
        paper_terms = set(keywords(paper.title + " " + paper.abstract, limit=20))
        for peer in peers:
            peer_terms = set(keywords(peer.title + " " + peer.abstract, limit=20))
            overlap = sorted(paper_terms & peer_terms)
            if overlap:
                overlaps.append({"paper_id": peer.paper_id, "shared_terms": overlap[:8], "score": len(overlap)})
        overlaps.sort(key=lambda item: item["score"], reverse=True)
        summary = f"Most comparable papers: {', '.join(item['paper_id'] for item in overlaps[:3]) or 'none in cohort'}."
        return AgentResult(self.name, paper.paper_id, summary, 0.72, {"comparables": overlaps[:5]})

    def compare(self, papers: Iterable[Paper]) -> ComparisonResult:
        paper_list = list(papers)
        dimensions: dict[str, dict[str, Any]] = {}
        for paper in paper_list:
            dimensions[paper.paper_id] = {
                "methods": [phrase for phrase, _ in keyphrases(paper.abstract, limit=5)],
                "benchmarks": MethodologyAgent()._benchmarks(paper),
                "limitations": WeaknessDetectorAgent().run(paper, AgentContext(paper_list, [])).findings["risks"],
                "compute_costs": [sentence for sentence in sentences(paper.abstract) if contains_any(sentence, MethodologyAgent.compute_markers)],
            }
        recommendation = "Prioritize papers with strong benchmark evidence and explicit reproducibility artifacts."
        return ComparisonResult([paper.paper_id for paper in paper_list], dimensions, recommendation)


class FlashcardAgent(ResearchAgent):
    """Generates active-recall flashcards from paper content."""

    name = AgentName.FLASHCARD

    def run(self, paper: Paper, context: AgentContext) -> AgentResult:
        cards = []
        for word in keywords(paper.title + " " + paper.abstract, limit=5):
            cards.append({"question": f"Why is '{word}' important in {paper.title}?", "answer": f"It is a recurring concept in the paper abstract and should be tied to the method or result."})
        cards.append({"question": f"What is the main contribution of {paper.title}?", "answer": centroid_summary(paper.abstract, max_sentences=1)})
        return AgentResult(self.name, paper.paper_id, f"Generated {len(cards)} flashcards.", 0.80, {"flashcards": cards})
