"""High-level V13 orchestration API."""

from __future__ import annotations

from dataclasses import dataclass, field

from .curriculum import CurriculumGenerator
from .models import EducationMode, Paper, TutoringTurn, V13EducationalExperience
from .tutoring import AdaptiveTutoringEngine


@dataclass
class V13Platform:
    """Paper-to-education facade used by apps, CLIs, and API handlers."""

    curriculum_generator: CurriculumGenerator = field(default_factory=CurriculumGenerator)
    tutoring_engine: AdaptiveTutoringEngine = field(init=False)

    def __post_init__(self) -> None:
        self.tutoring_engine = AdaptiveTutoringEngine(self.curriculum_generator)

    def generate(self, paper: Paper, mode: EducationMode | str) -> V13EducationalExperience:
        """Generate the complete V13 adaptive learning experience."""
        return self.curriculum_generator.generate_experience(paper, mode)

    def tutor(
        self,
        experience: V13EducationalExperience,
        learner_message: str,
        current_concept: str | None = None,
    ) -> TutoringTurn:
        """Run one adaptive tutoring turn against a generated experience."""
        return self.tutoring_engine.respond(experience, learner_message, current_concept)
