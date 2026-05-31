"""V8 literature review generation platform."""

from .citations import CitationFormatter
from .clustering import ClusteringPipeline
from .engine import LiteratureSynthesisEngine
from .models import Paper, Review, ReviewConfig
from .workflows import ReviewGenerationWorkflow

__all__ = [
    "CitationFormatter",
    "ClusteringPipeline",
    "LiteratureSynthesisEngine",
    "Paper",
    "Review",
    "ReviewConfig",
    "ReviewGenerationWorkflow",
]

__version__ = "8.0.0"
