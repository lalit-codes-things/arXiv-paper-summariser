"""Experiment planning workflows for V15 research simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .benchmark_prediction import BenchmarkPrediction, BenchmarkPredictionSystem
from .simulation_engine import ArchitectureSpec, ExperimentSpec, SimulationEngine, SimulationResult


@dataclass(frozen=True)
class ExperimentPlan:
    """Actionable plan generated from simulated research candidates."""

    objective: str
    selected_candidate: SimulationResult
    benchmark_predictions: list[BenchmarkPrediction]
    planning_steps: tuple[str, ...]
    acceptance_gates: tuple[str, ...]
    fallback_plan: str


class ExperimentPlanningWorkflow:
    """Coordinate simulation, benchmark prediction, and implementation planning."""

    def __init__(
        self,
        simulation_engine: SimulationEngine | None = None,
        benchmark_system: BenchmarkPredictionSystem | None = None,
    ) -> None:
        self.simulation_engine = simulation_engine or SimulationEngine()
        self.benchmark_system = benchmark_system or BenchmarkPredictionSystem()

    def generate_plan(
        self,
        objective: str,
        architectures: Iterable[ArchitectureSpec],
        experiment: ExperimentSpec,
    ) -> ExperimentPlan:
        """Simulate candidates and create the recommended experiment workflow."""

        simulations = [self.simulation_engine.run(architecture, experiment) for architecture in architectures]
        if not simulations:
            raise ValueError("At least one architecture is required to generate an experiment plan.")
        selected = self.benchmark_system.rank_candidates(simulations)[0]
        predictions = self.benchmark_system.predict(selected)
        return ExperimentPlan(
            objective=objective,
            selected_candidate=selected,
            benchmark_predictions=predictions,
            planning_steps=self._planning_steps(selected),
            acceptance_gates=self._acceptance_gates(selected),
            fallback_plan=self._fallback_plan(selected),
        )

    def build_research_backlog(self, plan: ExperimentPlan) -> list[dict[str, str]]:
        """Create an ordered backlog for implementing the selected experiment."""

        return [
            {
                "phase": "simulate",
                "task": "Archive V15 simulation result and benchmark confidence intervals.",
                "owner": "research",
            },
            {
                "phase": "prototype",
                "task": f"Prototype {plan.selected_candidate.architecture_name} with smallest viable dataset slice.",
                "owner": "ml-platform",
            },
            {
                "phase": "ablate",
                "task": "Run top ablations first: " + ", ".join(plan.selected_candidate.ablation_impacts),
                "owner": "evaluation",
            },
            {
                "phase": "gate",
                "task": "Compare observed metrics with predicted intervals before scaling compute.",
                "owner": "research-lead",
            },
        ]

    def _planning_steps(self, result: SimulationResult) -> tuple[str, ...]:
        return (
            "Freeze baseline metrics and dataset slice before writing production code.",
            f"Reserve {result.estimated_gpu_hours:.1f} GPU-hours and ${result.estimated_cost_usd:,.2f} budget.",
            "Implement instrumentation for quality, faithfulness, citation, latency, and cost metrics.",
            "Execute ablations in descending predicted impact before full benchmark runs.",
            "Promote implementation only if observed metrics land inside V15 prediction intervals.",
        )

    def _acceptance_gates(self, result: SimulationResult) -> tuple[str, ...]:
        return (
            f"Simulation confidence must remain >= {max(0.70, result.confidence - 0.05):.2f}.",
            f"Implementation risk must remain <= {min(0.75, result.implementation_risk + 0.10):.2f}.",
            "Observed benchmark regression must be explained by an approved ablation note.",
            "Actual compute spend must not exceed predicted cost by more than 15% without approval.",
        )

    def _fallback_plan(self, result: SimulationResult) -> str:
        if result.implementation_risk > 0.70:
            return "Reduce novelty and retrieval depth, then rerun V15 simulation before prototyping."
        if result.estimated_cost_usd > 20_000:
            return "Run a 10% dataset pilot and reuse checkpoint warm starts before full training."
        return "Proceed with a reduced-seed pilot if benchmark intervals are missed."
