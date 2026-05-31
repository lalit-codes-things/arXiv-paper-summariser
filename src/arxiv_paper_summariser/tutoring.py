"""Adaptive tutoring engine for paper-centered learning."""

from __future__ import annotations

from dataclasses import dataclass, field

from .curriculum import CurriculumGenerator
from .models import EducationMode, Paper, QuizQuestion, TutoringTurn, V13EducationalExperience

_CONFUSION_MARKERS = ("confused", "don't understand", "unclear", "stuck", "lost", "why")
_MASTERY_MARKERS = ("i know", "understand", "got it", "easy", "clear")


@dataclass
class AdaptiveTutoringEngine:
    """Stateful tutor that adapts scaffolding to learner level and responses."""

    curriculum_generator: CurriculumGenerator = field(default_factory=CurriculumGenerator)
    mastery_score: float = 0.5

    def start_session(self, paper: Paper, mode: EducationMode | str) -> V13EducationalExperience:
        """Create the initial adaptive learning bundle for a learner."""
        self.mastery_score = 0.5
        return self.curriculum_generator.generate_experience(paper, mode)

    def respond(
        self,
        experience: V13EducationalExperience,
        learner_message: str,
        current_concept: str | None = None,
    ) -> TutoringTurn:
        """Respond to a learner and optionally issue a targeted quiz question."""
        mode = experience.mode
        concept = current_concept or self._next_concept(experience)
        lowered = learner_message.lower()
        if any(marker in lowered for marker in _CONFUSION_MARKERS):
            self.mastery_score = max(0.0, self.mastery_score - 0.1)
            response = self._scaffolded_response(concept, mode)
            next_step = f"Review prerequisites for {concept}, then answer a low-stakes check."
            quiz = self._quiz_for(experience, concept)
        elif any(marker in lowered for marker in _MASTERY_MARKERS):
            self.mastery_score = min(1.0, self.mastery_score + 0.1)
            response = self._extension_response(concept, mode)
            next_step = f"Advance to the next roadmap milestone after {concept}."
            quiz = None
        else:
            response = self._socratic_response(concept, mode)
            next_step = f"State the paper problem that {concept} helps solve."
            quiz = self._quiz_for(experience, concept) if self.mastery_score < 0.7 else None
        return TutoringTurn(
            learner_message=learner_message,
            tutor_response=response,
            recommended_next_step=next_step,
            confidence=round(self.mastery_score, 2),
            quiz=quiz,
        )

    def _next_concept(self, experience: V13EducationalExperience) -> str:
        ordered = experience.concept_graph.ordered_concepts()
        if not ordered:
            return "the paper's central claim"
        index = min(int(self.mastery_score * len(ordered)), len(ordered) - 1)
        return ordered[index]

    def _quiz_for(self, experience: V13EducationalExperience, concept: str) -> QuizQuestion | None:
        for question in experience.diagnostic_quiz:
            if question.answer == concept:
                return question
        return experience.diagnostic_quiz[0] if experience.diagnostic_quiz else None

    def _scaffolded_response(self, concept: str, mode: EducationMode) -> str:
        if mode is EducationMode.BEGINNER:
            return f"Let's slow down: {concept} is one building block. First say it in everyday words, then connect it to the paper's goal."
        return f"Let's isolate {concept}: identify its inputs, assumptions, and output before reconnecting it to the full argument."

    def _extension_response(self, concept: str, mode: EducationMode) -> str:
        if mode is EducationMode.RESEARCHER:
            return f"Great. Now critique {concept}: what baseline, limitation, or open problem would test the paper's claim?"
        return f"Great. Now teach {concept} back using a new example and note one edge case."

    def _socratic_response(self, concept: str, mode: EducationMode) -> str:
        if mode is EducationMode.BEGINNER:
            return f"What do you think {concept} is trying to help the authors explain?"
        return f"Which assumption makes {concept} useful in this paper, and when might that assumption fail?"
