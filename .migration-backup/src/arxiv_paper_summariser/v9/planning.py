"""Implementation planning for V9 outputs."""

from __future__ import annotations

from .models import ArchitectureGraph, DependencyReport, ImplementationTask, PseudoCodeBlock


class ImplementationPlanner:
    """Turn paper understanding into an ordered implementation checklist."""

    def plan(
        self,
        pseudo_code: list[PseudoCodeBlock],
        architecture: ArchitectureGraph,
        dependencies: DependencyReport,
    ) -> list[ImplementationTask]:
        tasks = [
            ImplementationTask(
                "Create reproducible project scaffold",
                "Create src, configs, scripts, tests, and artifact directories with pinned runtime metadata.",
                "Starter repository layout",
            ),
            ImplementationTask(
                "Prepare datasets",
                f"Implement dataset loaders and validation for: {', '.join(dependencies.datasets)}.",
                "Dataset module with smoke tests",
            ),
        ]
        for component in architecture.components:
            tasks.append(
                ImplementationTask(
                    f"Implement {component.name}",
                    f"Build the {component.kind} component. Evidence: {component.evidence[:180]}",
                    f"{component.name} implementation and unit test",
                )
            )
        for block in pseudo_code:
            tasks.append(
                ImplementationTask(
                    f"Translate {block.title}",
                    "Implement procedure steps: " + " ".join(block.steps[:5]),
                    "Executable training/evaluation function",
                )
            )
        tasks.extend(
            [
                ImplementationTask(
                    "Wire training pipeline",
                    "Connect data, model, loss, optimizer, metrics, checkpointing, and configuration.",
                    "scripts/train.py runnable with configs/experiment.yaml",
                ),
                ImplementationTask(
                    "Validate reproducibility",
                    "Run seed stability, ablation, dependency, and artifact checks before claiming parity.",
                    "Reproducibility report",
                    priority="should",
                ),
            ]
        )
        return tasks

    @staticmethod
    def checklist(tasks: list[ImplementationTask]) -> str:
        lines = ["# Implementation Checklist", ""]
        for task in tasks:
            lines.append(f"- [ ] **{task.title}** ({task.priority}) — {task.deliverable}")
            lines.append(f"  - {task.description}")
        return "\n".join(lines) + "\n"
