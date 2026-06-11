"""Experiment configuration generation."""

from __future__ import annotations

from .models import DependencyReport, ExperimentSpec
from .text import slugify


class ExperimentGenerator:
    """Generate baseline, ablation, and reproduction experiment specs."""

    def generate(self, dependencies: DependencyReport) -> list[ExperimentSpec]:
        primary_dataset = dependencies.datasets[0]
        primary_metric = dependencies.metrics[0]
        specs = [
            ExperimentSpec(
                name="baseline_reproduction",
                dataset=primary_dataset,
                metric=primary_metric,
                knobs={"seed": 1337, "epochs": 10, "batch_size": 32, "learning_rate": 0.001},
                command="python scripts/train.py --config configs/baseline_reproduction.yaml",
            ),
            ExperimentSpec(
                name="seed_sweep",
                dataset=primary_dataset,
                metric=primary_metric,
                knobs={"seed": [1, 2, 3, 5, 8], "epochs": 10, "batch_size": 32},
                command="python scripts/train.py --config configs/seed_sweep.yaml",
            ),
            ExperimentSpec(
                name="core_ablation",
                dataset=primary_dataset,
                metric=primary_metric,
                knobs={"disable_components": ["attention", "augmentation", "regularization"], "epochs": 10},
                command="python scripts/train.py --config configs/core_ablation.yaml",
            ),
        ]
        return specs

    @staticmethod
    def to_yaml(specs: list[ExperimentSpec]) -> str:
        lines = ["experiments:"]
        for spec in specs:
            lines.extend(
                [
                    f"  - name: {slugify(spec.name)}",
                    f"    dataset: {spec.dataset}",
                    f"    metric: {spec.metric}",
                    f"    command: {spec.command}",
                    "    knobs:",
                ]
            )
            for key, value in spec.knobs.items():
                lines.append(f"      {key}: {value}")
        return "\n".join(lines) + "\n"
