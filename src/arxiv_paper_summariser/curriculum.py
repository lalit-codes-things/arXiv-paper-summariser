"""Curriculum generation for V13 adaptive paper experiences."""

from __future__ import annotations

from dataclasses import dataclass, field

from .concept_graph import ConceptGraphPipeline
from .models import (
    ConceptGraph,
    EducationMode,
    Explanation,
    LearningRoadmap,
    Lesson,
    MiniCourse,
    Paper,
    QuizQuestion,
    V13EducationalExperience,
)

_MODE_DEPTH = {
    EducationMode.BEGINNER: "intuitive, analogy-heavy, low math",
    EducationMode.UNDERGRADUATE: "conceptual with light equations and examples",
    EducationMode.GRAD_STUDENT: "technical with assumptions, derivations, and trade-offs",
    EducationMode.RESEARCHER: "research-contextual with novelty, limitations, and open problems",
}

_MODE_HOURS = {
    EducationMode.BEGINNER: 6.0,
    EducationMode.UNDERGRADUATE: 4.5,
    EducationMode.GRAD_STUDENT: 3.0,
    EducationMode.RESEARCHER: 2.0,
}


@dataclass
class CurriculumGenerator:
    """Generate explanations, roadmaps, quizzes, and mini-courses from a paper."""

    graph_pipeline: ConceptGraphPipeline = field(default_factory=ConceptGraphPipeline)

    def generate_explanations(self, graph: ConceptGraph, mode: EducationMode | str) -> tuple[Explanation, ...]:
        mode = EducationMode.coerce(mode)
        explanations = []
        for concept in graph.concepts:
            explanations.append(
                Explanation(
                    concept=concept.name,
                    mode=mode,
                    text=self._explain(concept.name, concept.prerequisites, mode),
                    analogy=self._analogy(concept.name, mode),
                    technical_depth=_MODE_DEPTH[mode],
                )
            )
        return tuple(explanations)

    def generate_prerequisites(self, graph: ConceptGraph) -> tuple[str, ...]:
        prerequisites: list[str] = []
        for concept in graph.concepts:
            prerequisites.extend(concept.prerequisites)
        return tuple(dict.fromkeys(prerequisites))

    def generate_quiz(self, graph: ConceptGraph, mode: EducationMode | str, limit: int = 5) -> tuple[QuizQuestion, ...]:
        mode = EducationMode.coerce(mode)
        questions: list[QuizQuestion] = []
        ordered = graph.ordered_concepts()
        for index, concept in enumerate(ordered[:limit]):
            distractors = tuple(other for other in ordered if other != concept)[:3]
            options = (concept, *distractors) if distractors else (concept, "not enough context")
            questions.append(
                QuizQuestion(
                    prompt=f"In this paper, what role does '{concept}' most likely play?",
                    options=options,
                    answer=concept,
                    explanation=f"'{concept}' is a central concept connected to the paper's learning path at step {index + 1}.",
                    difficulty=mode,
                )
            )
        return tuple(questions)

    def generate_roadmap(self, graph: ConceptGraph, mode: EducationMode | str) -> LearningRoadmap:
        mode = EducationMode.coerce(mode)
        ordered = graph.ordered_concepts()
        milestones = tuple(f"Master {concept}" for concept in ordered)
        checkpoints = tuple(f"Explain how {concept} supports the paper's contribution" for concept in ordered[:5])
        return LearningRoadmap(
            mode=mode,
            milestones=milestones,
            estimated_hours=max(_MODE_HOURS[mode], len(ordered) * 0.35),
            checkpoints=checkpoints,
        )

    def generate_mini_course(self, paper: Paper, graph: ConceptGraph, mode: EducationMode | str) -> MiniCourse:
        mode = EducationMode.coerce(mode)
        ordered = graph.ordered_concepts()
        quiz = self.generate_quiz(graph, mode, limit=3)
        lessons: list[Lesson] = []
        for chunk_index, start in enumerate(range(0, len(ordered), 3), start=1):
            concepts = ordered[start : start + 3]
            title = f"Module {chunk_index}: {' + '.join(concepts[:2])}"
            lessons.append(
                Lesson(
                    title=title,
                    objectives=tuple(f"Describe {concept}" for concept in concepts),
                    concepts=concepts,
                    explanation=f"A {_MODE_DEPTH[mode]} lesson connecting {', '.join(concepts)} to '{paper.title}'.",
                    quiz=quiz[:1],
                )
            )
        return MiniCourse(
            title=f"Mini-course: {paper.title}",
            mode=mode,
            lessons=tuple(lessons),
            capstone="Create a teach-back summary that links the concept graph to the paper's main claim.",
        )

    def generate_experience(self, paper: Paper, mode: EducationMode | str) -> V13EducationalExperience:
        mode = EducationMode.coerce(mode)
        graph = self.graph_pipeline.run(paper)
        return V13EducationalExperience(
            paper_title=paper.title,
            mode=mode,
            concept_graph=graph,
            explanations=self.generate_explanations(graph, mode),
            prerequisites=self.generate_prerequisites(graph),
            roadmap=self.generate_roadmap(graph, mode),
            mini_course=self.generate_mini_course(paper, graph, mode),
            diagnostic_quiz=self.generate_quiz(graph, mode),
        )

    def _explain(self, concept: str, prerequisites: tuple[str, ...], mode: EducationMode) -> str:
        prereq_text = ", ".join(prerequisites)
        if mode is EducationMode.BEGINNER:
            return f"Think of {concept} as a key idea. Start with {prereq_text}, then ask what problem it helps solve."
        if mode is EducationMode.UNDERGRADUATE:
            return f"{concept} connects the paper's assumptions to its method; review {prereq_text} and trace inputs to outputs."
        if mode is EducationMode.GRAD_STUDENT:
            return f"Analyze {concept} through its assumptions, objective function, and failure modes after reviewing {prereq_text}."
        return f"Position {concept} against prior work, inspect novelty claims, and evaluate limitations relative to {prereq_text}."

    def _analogy(self, concept: str, mode: EducationMode) -> str | None:
        if mode is EducationMode.RESEARCHER:
            return None
        return f"{concept} is like a map marker: it helps the learner know where they are in the paper's argument."
