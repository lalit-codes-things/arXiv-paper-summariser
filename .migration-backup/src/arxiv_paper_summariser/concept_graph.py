"""Concept extraction and dependency graph generation pipelines."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .models import Concept, ConceptDependency, ConceptGraph, Paper

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9-]{2,}")
_PHRASE_RE = re.compile(r"\b(?:[A-Z][a-z0-9-]+|[a-z]+(?:-[a-z]+)+)(?:\s+(?:[A-Z][a-z0-9-]+|[a-z]+(?:-[a-z]+)+)){0,3}\b")

_STOPWORDS = {
    "about",
    "after",
    "also",
    "analysis",
    "approach",
    "based",
    "between",
    "could",
    "data",
    "different",
    "during",
    "each",
    "effects",
    "from",
    "into",
    "method",
    "model",
    "paper",
    "results",
    "show",
    "study",
    "such",
    "that",
    "their",
    "these",
    "this",
    "using",
    "with",
    "within",
}

_FOUNDATIONAL_HINTS = (
    "probability",
    "linear algebra",
    "calculus",
    "optimization",
    "statistics",
    "graph theory",
    "machine learning",
    "neural network",
    "algorithm",
)

_RESEARCH_HINTS = (
    "theorem",
    "proof",
    "architecture",
    "benchmark",
    "ablation",
    "estimator",
    "posterior",
    "transformer",
    "diffusion",
    "embedding",
)


@dataclass(frozen=True)
class ConceptGraphPipeline:
    """Build dependency-first concept graphs from paper text.

    The implementation is deterministic and dependency-free so it can be used in
    tests, local previews, or as a fallback when an LLM extraction service is not
    available. The API is intentionally narrow: richer extractors can be adapted
    by returning the same ``ConceptGraph`` model.
    """

    max_concepts: int = 12

    def extract_concepts(self, paper: Paper) -> tuple[Concept, ...]:
        candidates = self._candidate_terms(paper)
        weighted = Counter(candidates)
        for keyword in paper.keywords:
            keyword = self._clean(keyword)
            if keyword:
                weighted[keyword] += 5

        concepts: list[Concept] = []
        for name, weight in weighted.most_common(self.max_concepts):
            evidence = self._evidence_for(name, paper.full_text)
            concepts.append(
                Concept(
                    name=name,
                    weight=weight,
                    evidence=evidence,
                    prerequisites=self.generate_prerequisites(name),
                )
            )
        return tuple(concepts)

    def generate_prerequisites(self, concept: str) -> tuple[str, ...]:
        lowered = concept.lower()
        prerequisites: list[str] = []
        if any(hint in lowered for hint in ("neural", "transformer", "embedding", "diffusion")):
            prerequisites.extend(["machine learning", "linear algebra", "optimization"])
        if any(hint in lowered for hint in ("posterior", "bayesian", "probabilistic", "estimator")):
            prerequisites.extend(["probability", "statistics"])
        if any(hint in lowered for hint in ("graph", "dependency", "network")):
            prerequisites.append("graph theory")
        if not prerequisites:
            prerequisites.append("core terminology")
        return tuple(dict.fromkeys(prerequisites))

    def build_dependencies(self, concepts: tuple[Concept, ...]) -> tuple[ConceptDependency, ...]:
        names = [concept.name for concept in concepts]
        foundational = [name for name in names if self._is_foundational(name)]
        advanced = [name for name in names if self._is_advanced(name)]
        dependencies: list[ConceptDependency] = []

        for target in advanced:
            for source in foundational[:3]:
                if source != target:
                    dependencies.append(ConceptDependency(source=source, target=target, strength=0.85))

        for earlier, later in zip(names, names[1:]):
            if not any(edge.source == earlier and edge.target == later for edge in dependencies):
                dependencies.append(ConceptDependency(source=earlier, target=later, strength=0.55))

        return tuple(dependencies)

    def run(self, paper: Paper) -> ConceptGraph:
        concepts = self.extract_concepts(paper)
        return ConceptGraph(concepts=concepts, dependencies=self.build_dependencies(concepts))

    def _candidate_terms(self, paper: Paper) -> list[str]:
        text = paper.full_text
        phrases = [self._clean(match.group(0)) for match in _PHRASE_RE.finditer(text)]
        tokens = [self._clean(match.group(0)) for match in _TOKEN_RE.finditer(text)]
        candidates = [term for term in phrases + tokens if self._is_useful(term)]
        return candidates

    def _evidence_for(self, concept: str, text: str) -> tuple[str, ...]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        matches = [sentence.strip() for sentence in sentences if concept.lower() in sentence.lower()]
        return tuple(matches[:2])

    def _clean(self, value: str) -> str:
        return re.sub(r"\s+", " ", value.strip(" .,:;()[]{}\n\t")).lower()

    def _is_useful(self, term: str) -> bool:
        if len(term) < 4 or term in _STOPWORDS:
            return False
        if term.isdigit():
            return False
        return not all(part in _STOPWORDS for part in term.split())

    def _is_foundational(self, concept: str) -> bool:
        lowered = concept.lower()
        return any(hint in lowered for hint in _FOUNDATIONAL_HINTS)

    def _is_advanced(self, concept: str) -> bool:
        lowered = concept.lower()
        return any(hint in lowered for hint in _RESEARCH_HINTS)
