"""Shared V9 data models.

The models intentionally use only the Python standard library so the platform can
bootstrap starter repositories before project-specific dependencies are known.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PseudoCodeBlock:
    """A paper algorithm or procedure normalized for implementation."""

    title: str
    steps: list[str]
    source_heading: str = ""


@dataclass(frozen=True)
class ArchitectureComponent:
    """A model, module, data, or training component inferred from the paper."""

    name: str
    kind: str
    evidence: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ArchitectureGraph:
    """A lightweight architecture graph suitable for code skeleton generation."""

    components: list[ArchitectureComponent]
    edges: list[tuple[str, str, str]]


@dataclass(frozen=True)
class DependencyReport:
    """Dependencies and environment hints detected in paper text."""

    python_packages: list[str]
    datasets: list[str]
    hardware: list[str]
    metrics: list[str]
    external_tools: list[str]


@dataclass(frozen=True)
class ImplementationTask:
    """A concrete engineering task derived from the paper."""

    title: str
    description: str
    deliverable: str
    priority: str = "must"


@dataclass(frozen=True)
class ExperimentSpec:
    """Runnable experiment configuration derived from claims and metrics."""

    name: str
    dataset: str
    metric: str
    knobs: dict[str, Any]
    command: str


@dataclass(frozen=True)
class ReproducibilityFinding:
    """A reproducibility risk or supporting implementation detail."""

    category: str
    status: str
    detail: str
    mitigation: str


@dataclass(frozen=True)
class GeneratedFile:
    """A generated repository file."""

    path: str
    content: str


@dataclass(frozen=True)
class V9WorkflowResult:
    """Complete paper-to-implementation output bundle."""

    pseudo_code: list[PseudoCodeBlock]
    architecture: ArchitectureGraph
    dependencies: DependencyReport
    implementation_plan: list[ImplementationTask]
    experiments: list[ExperimentSpec]
    reproducibility: list[ReproducibilityFinding]
    starter_repo: list[GeneratedFile]
    checklist_markdown: str
    experiment_config_yaml: str
    training_pipeline: str
