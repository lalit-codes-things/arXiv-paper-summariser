"""Deterministic simulation primitives for V15 research planning.

The engine estimates research outcomes before implementation by combining an
architecture profile, experiment configuration, and compute prices into a
repeatable scorecard. It intentionally uses transparent heuristics rather than a
black-box model so that planning decisions are auditable in pull requests and
research reviews.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import log10, sqrt
from typing import Mapping


@dataclass(frozen=True)
class ArchitectureSpec:
    """A candidate architecture to evaluate before implementation."""

    name: str
    encoder_layers: int
    decoder_layers: int
    hidden_size: int
    retrieval_depth: int = 0
    context_window: int = 8_192
    quantization_bits: int = 16
    parameter_count_millions: float = 250.0
    novelty_factor: float = 0.5

    def complexity_index(self) -> float:
        """Return a normalized complexity estimate for cost/risk modeling."""

        layer_term = (self.encoder_layers + self.decoder_layers) / 24
        hidden_term = self.hidden_size / 768
        retrieval_term = 1 + min(self.retrieval_depth, 20) / 40
        context_term = sqrt(max(self.context_window, 1) / 8_192)
        parameter_term = sqrt(max(self.parameter_count_millions, 1) / 250)
        quantization_discount = max(0.45, self.quantization_bits / 16)
        return layer_term * hidden_term * retrieval_term * context_term * parameter_term * quantization_discount


@dataclass(frozen=True)
class ExperimentSpec:
    """Planned experiment settings that affect time, cost, and confidence."""

    name: str
    dataset_size: int
    training_steps: int
    evaluation_samples: int
    seeds: int = 3
    gpu_type: str = "A100"
    gpu_count: int = 1
    target_metrics: tuple[str, ...] = ("rouge_l", "faithfulness", "latency")
    ablations: tuple[str, ...] = ("retrieval", "reranking", "compression")


@dataclass(frozen=True)
class ComputeProfile:
    """Runtime and pricing assumptions for experiment simulation."""

    hourly_gpu_prices: Mapping[str, float] = field(
        default_factory=lambda: {
            "T4": 0.35,
            "L4": 0.80,
            "A10G": 1.10,
            "A100": 3.20,
            "H100": 5.90,
        }
    )
    engineering_hourly_rate: float = 110.0
    storage_cost_per_gb_month: float = 0.023

    def price_for(self, gpu_type: str) -> float:
        """Return hourly GPU price, falling back to A100 pricing."""

        return self.hourly_gpu_prices.get(gpu_type.upper(), self.hourly_gpu_prices["A100"])


@dataclass(frozen=True)
class SimulationResult:
    """Outcome estimates for a planned research experiment."""

    architecture_name: str
    experiment_name: str
    quality_score: float
    confidence: float
    estimated_gpu_hours: float
    estimated_cost_usd: float
    implementation_risk: float
    ablation_impacts: dict[str, float]
    benchmark_predictions: dict[str, float]
    recommendation: str


class SimulationEngine:
    """Simulate architecture and experiment outcomes before implementation."""

    def __init__(self, compute_profile: ComputeProfile | None = None) -> None:
        self.compute_profile = compute_profile or ComputeProfile()

    def simulate_architecture(self, architecture: ArchitectureSpec) -> dict[str, float]:
        """Estimate architecture quality, risk, and throughput characteristics."""

        complexity = architecture.complexity_index()
        retrieval_bonus = min(0.16, architecture.retrieval_depth * 0.012)
        context_bonus = min(0.12, log10(max(architecture.context_window, 1)) / 40)
        novelty_bonus = min(0.10, architecture.novelty_factor * 0.08)
        compression_penalty = max(0.0, (16 - architecture.quantization_bits) * 0.006)
        quality = self._clamp(0.58 + retrieval_bonus + context_bonus + novelty_bonus - compression_penalty, 0.0, 0.98)
        risk = self._clamp(0.18 + complexity * 0.22 + architecture.novelty_factor * 0.18, 0.05, 0.92)
        throughput = self._clamp(1_000 / max(complexity, 0.1), 30.0, 5_000.0)
        return {
            "complexity_index": round(complexity, 4),
            "expected_quality": round(quality, 4),
            "implementation_risk": round(risk, 4),
            "tokens_per_second": round(throughput, 2),
        }

    def estimate_experiment(self, architecture: ArchitectureSpec, experiment: ExperimentSpec) -> dict[str, float]:
        """Estimate runtime, direct cloud cost, and review confidence."""

        architecture_projection = self.simulate_architecture(architecture)
        complexity = architecture_projection["complexity_index"]
        data_scale = max(experiment.dataset_size, 1) / 100_000
        step_scale = max(experiment.training_steps, 1) / 10_000
        seed_scale = max(experiment.seeds, 1)
        parallel_efficiency = 0.72 + min(experiment.gpu_count, 16) * 0.025
        gpu_hours = complexity * data_scale * step_scale * seed_scale * 180 / max(parallel_efficiency, 0.1)
        eval_hours = experiment.evaluation_samples * len(experiment.target_metrics) * complexity / 20_000
        total_gpu_hours = gpu_hours + eval_hours
        infra_cost = total_gpu_hours * experiment.gpu_count * self.compute_profile.price_for(experiment.gpu_type)
        engineering_hours = 6 + len(experiment.ablations) * 2.5 + len(experiment.target_metrics) * 1.5
        storage_gb_month = experiment.dataset_size * 0.000_015 * max(experiment.seeds, 1)
        total_cost = infra_cost + engineering_hours * self.compute_profile.engineering_hourly_rate + storage_gb_month * self.compute_profile.storage_cost_per_gb_month
        confidence = self._clamp(0.42 + min(experiment.evaluation_samples, 20_000) / 45_000 + min(experiment.seeds, 5) * 0.055, 0.1, 0.96)
        return {
            "estimated_gpu_hours": round(total_gpu_hours, 2),
            "estimated_cost_usd": round(total_cost, 2),
            "confidence": round(confidence, 4),
            "engineering_hours": round(engineering_hours, 2),
        }

    def simulate_ablation(self, architecture: ArchitectureSpec, experiment: ExperimentSpec) -> dict[str, float]:
        """Estimate metric deltas when planned components are removed."""

        architecture_projection = self.simulate_architecture(architecture)
        base_quality = architecture_projection["expected_quality"]
        impact_catalog = {
            "retrieval": 0.025 + min(architecture.retrieval_depth, 12) * 0.006,
            "reranking": 0.018 + architecture.novelty_factor * 0.012,
            "compression": -0.010 if architecture.quantization_bits <= 8 else 0.008,
            "long_context": min(0.045, architecture.context_window / 1_000_000),
            "distillation": 0.020 + min(0.025, architecture.parameter_count_millions / 20_000),
            "citation_grounding": 0.038,
        }
        return {
            ablation: round(self._clamp(impact_catalog.get(ablation, base_quality * 0.035), -0.08, 0.16), 4)
            for ablation in experiment.ablations
        }

    def run(self, architecture: ArchitectureSpec, experiment: ExperimentSpec) -> SimulationResult:
        """Generate a complete simulation result for a candidate experiment."""

        architecture_projection = self.simulate_architecture(architecture)
        experiment_projection = self.estimate_experiment(architecture, experiment)
        ablation_impacts = self.simulate_ablation(architecture, experiment)
        benchmark_predictions = self._predict_benchmarks(architecture_projection, experiment_projection, ablation_impacts)
        quality_score = self._composite_quality_score(benchmark_predictions)
        risk = architecture_projection["implementation_risk"]
        recommendation = self._recommend(quality_score, experiment_projection["estimated_cost_usd"], risk)
        return SimulationResult(
            architecture_name=architecture.name,
            experiment_name=experiment.name,
            quality_score=quality_score,
            confidence=experiment_projection["confidence"],
            estimated_gpu_hours=experiment_projection["estimated_gpu_hours"],
            estimated_cost_usd=experiment_projection["estimated_cost_usd"],
            implementation_risk=risk,
            ablation_impacts=ablation_impacts,
            benchmark_predictions=benchmark_predictions,
            recommendation=recommendation,
        )

    def _predict_benchmarks(
        self,
        architecture_projection: Mapping[str, float],
        experiment_projection: Mapping[str, float],
        ablation_impacts: Mapping[str, float],
    ) -> dict[str, float]:
        quality = architecture_projection["expected_quality"]
        confidence = experiment_projection["confidence"]
        ablation_signal = sum(max(value, 0) for value in ablation_impacts.values()) / max(len(ablation_impacts), 1)
        return {
            "rouge_l": round(self._clamp(41 + quality * 18 + ablation_signal * 42, 0, 100), 3),
            "faithfulness": round(self._clamp(0.60 + quality * 0.24 + confidence * 0.08, 0, 1), 4),
            "citation_f1": round(self._clamp(0.48 + quality * 0.30 + ablation_signal * 0.45, 0, 1), 4),
            "latency_p95_ms": round(self._clamp(2_400 / max(architecture_projection["tokens_per_second"], 1) * 100, 50, 15_000), 2),
        }

    def _composite_quality_score(self, benchmark_predictions: Mapping[str, float]) -> float:
        rouge = benchmark_predictions.get("rouge_l", 0.0)
        faithfulness = benchmark_predictions.get("faithfulness", 0.0) * 100
        citation_f1 = benchmark_predictions.get("citation_f1", 0.0) * 100
        latency = benchmark_predictions.get("latency_p95_ms", 1_000.0)
        latency_score = self._clamp(100 - latency / 150, 0, 100)
        composite = rouge * 0.35 + faithfulness * 0.30 + citation_f1 * 0.25 + latency_score * 0.10
        return round(composite, 4)

    def _recommend(self, quality_score: float, cost: float, risk: float) -> str:
        if risk > 0.75:
            return "Revise architecture before implementation; risk exceeds V15 tolerance."
        if cost > 25_000 and quality_score < 65:
            return "Downscope experiment or run a smaller pilot before full implementation."
        if quality_score >= 72 and risk <= 0.65:
            return "Proceed with implementation after validating top ablations."
        return "Run a pilot simulation with reduced data and additional seeds."

    @staticmethod
    def _clamp(value: float, lower: float, upper: float) -> float:
        return max(lower, min(upper, value))
