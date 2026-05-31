"""Core V13 data models for adaptive educational paper experiences."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class EducationMode(str, Enum):
    """Supported learner profiles for explain-by-level experiences."""

    BEGINNER = "beginner"
    UNDERGRADUATE = "undergraduate"
    GRAD_STUDENT = "grad student"
    RESEARCHER = "researcher"

    @classmethod
    def coerce(cls, value: "EducationMode | str") -> "EducationMode":
        if isinstance(value, cls):
            return value
        normalised = value.strip().lower().replace("_", " ").replace("-", " ")
        aliases = {
            "grad": cls.GRAD_STUDENT,
            "graduate": cls.GRAD_STUDENT,
            "graduate student": cls.GRAD_STUDENT,
            "undergrad": cls.UNDERGRADUATE,
        }
        if normalised in aliases:
            return aliases[normalised]
        for mode in cls:
            if mode.value == normalised:
                return mode
        allowed = ", ".join(mode.value for mode in cls)
        raise ValueError(f"Unsupported education mode {value!r}; expected one of: {allowed}")


@dataclass(frozen=True)
class Paper:
    """A parsed paper payload used by V13 pipelines."""

    title: str
    abstract: str
    sections: dict[str, str] = field(default_factory=dict)
    keywords: tuple[str, ...] = ()

    @property
    def full_text(self) -> str:
        body = "\n\n".join(self.sections.values())
        return f"{self.title}\n\n{self.abstract}\n\n{body}".strip()

    @classmethod
    def from_text(
        cls,
        title: str,
        abstract: str,
        body: str = "",
        keywords: Iterable[str] = (),
    ) -> "Paper":
        sections = {"body": body} if body else {}
        return cls(title=title, abstract=abstract, sections=sections, keywords=tuple(keywords))


@dataclass(frozen=True)
class Concept:
    """An extracted concept and lightweight pedagogical metadata."""

    name: str
    weight: int = 1
    evidence: tuple[str, ...] = ()
    prerequisites: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConceptDependency:
    """Directed edge representing that source should be learned before target."""

    source: str
    target: str
    relationship: str = "prerequisite"
    strength: float = 1.0


@dataclass(frozen=True)
class ConceptGraph:
    """Dependency graph for paper concepts."""

    concepts: tuple[Concept, ...]
    dependencies: tuple[ConceptDependency, ...]

    def ordered_concepts(self) -> tuple[str, ...]:
        """Return concepts in dependency-first order using a deterministic topological pass."""
        names = [concept.name for concept in self.concepts]
        incoming = {name: 0 for name in names}
        outgoing: dict[str, list[str]] = {name: [] for name in names}
        for dependency in self.dependencies:
            if dependency.source in incoming and dependency.target in incoming:
                incoming[dependency.target] += 1
                outgoing[dependency.source].append(dependency.target)

        queue = [name for name in names if incoming[name] == 0]
        ordered: list[str] = []
        while queue:
            current = queue.pop(0)
            ordered.append(current)
            for target in sorted(outgoing[current]):
                incoming[target] -= 1
                if incoming[target] == 0:
                    queue.append(target)
        ordered.extend(name for name in names if name not in ordered)
        return tuple(ordered)


@dataclass(frozen=True)
class Explanation:
    concept: str
    mode: EducationMode
    text: str
    analogy: str | None = None
    technical_depth: str = "medium"


@dataclass(frozen=True)
class QuizQuestion:
    prompt: str
    options: tuple[str, ...]
    answer: str
    explanation: str
    difficulty: EducationMode


@dataclass(frozen=True)
class Lesson:
    title: str
    objectives: tuple[str, ...]
    concepts: tuple[str, ...]
    explanation: str
    quiz: tuple[QuizQuestion, ...] = ()


@dataclass(frozen=True)
class MiniCourse:
    title: str
    mode: EducationMode
    lessons: tuple[Lesson, ...]
    capstone: str


@dataclass(frozen=True)
class LearningRoadmap:
    mode: EducationMode
    milestones: tuple[str, ...]
    estimated_hours: float
    checkpoints: tuple[str, ...]


@dataclass(frozen=True)
class TutoringTurn:
    learner_message: str
    tutor_response: str
    recommended_next_step: str
    confidence: float
    quiz: QuizQuestion | None = None


@dataclass(frozen=True)
class V13EducationalExperience:
    """Complete V13 paper-to-learning artifact."""

    paper_title: str
    mode: EducationMode
    concept_graph: ConceptGraph
    explanations: tuple[Explanation, ...]
    prerequisites: tuple[str, ...]
    roadmap: LearningRoadmap
    mini_course: MiniCourse
    diagnostic_quiz: tuple[QuizQuestion, ...]
