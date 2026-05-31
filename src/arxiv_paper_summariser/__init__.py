"""Adaptive educational experience generation for arXiv papers (V13)."""

from .concept_graph import ConceptGraphPipeline
from .curriculum import CurriculumGenerator
from .models import EducationMode, Paper, V13EducationalExperience
from .platform import V13Platform
from .tutoring import AdaptiveTutoringEngine

__all__ = [
    "AdaptiveTutoringEngine",
    "ConceptGraphPipeline",
    "CurriculumGenerator",
    "EducationMode",
    "Paper",
    "V13Platform",
    "V13EducationalExperience",
]

__version__ = "13.0.0"
