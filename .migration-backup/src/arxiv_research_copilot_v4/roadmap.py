"""Research roadmap generation utilities."""

from __future__ import annotations

from .models import Paper, RoadmapStep
from .text import keywords


class RoadmapGenerator:
    """Generate learning paths such as 'How to learn diffusion models'."""

    def generate(self, objective: str, papers: list[Paper], *, steps: int = 6) -> list[RoadmapStep]:
        """Create an ordered roadmap grounded in the supplied papers."""

        topic = objective.replace("How to learn", "").strip() or objective
        sorted_papers = sorted(papers, key=lambda paper: paper.published)
        modules = [
            ("Orientation", f"Define the scope of {topic} and map core terminology."),
            ("Foundations", f"Study prerequisite math, architectures, and datasets for {topic}."),
            ("Seminal papers", "Read older or highly connected papers before implementation."),
            ("Implementation", "Reproduce a baseline and document design choices."),
            ("Evaluation", "Compare benchmarks, limitations, and compute costs."),
            ("Frontier", "Track emerging trends and open research questions."),
        ][:steps]
        roadmap: list[RoadmapStep] = []
        for index, (title, objective_text) in enumerate(modules, start=1):
            evidence = sorted_papers[max(0, index - 2) : index + 1]
            if not evidence:
                evidence = sorted_papers[:2]
            deliverable = "Reading notes" if index <= 3 else "Prototype or benchmark table"
            roadmap.append(RoadmapStep(index, title, objective_text, [paper.paper_id for paper in evidence], deliverable))
        return roadmap

    def prerequisites(self, objective: str, papers: list[Paper]) -> list[str]:
        """Infer prerequisite topics from the corpus."""

        corpus = " ".join(paper.title + " " + paper.abstract for paper in papers) + " " + objective
        return keywords(corpus, limit=12)
