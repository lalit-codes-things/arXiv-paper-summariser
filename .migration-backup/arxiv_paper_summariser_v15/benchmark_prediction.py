"""Benchmark prediction system for V15 simulation outputs."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Iterable, Mapping

from .simulation_engine import SimulationResult


@dataclass(frozen=True)
class BenchmarkPrediction:
    """Predicted benchmark value with confidence interval and rationale."""

    metric: str
    expected_value: float
    lower_bound: float
    upper_bound: float
    confidence: float
    rationale: str


class BenchmarkPredictionSystem:
    """Turn simulation results into benchmark forecasts and rankings."""

    def predict(self, result: SimulationResult) -> list[BenchmarkPrediction]:
        """Create calibrated prediction intervals for each benchmark metric."""

        predictions: list[BenchmarkPrediction] = []
        uncertainty = max(0.02, (1 - result.confidence) * 0.18 + result.implementation_risk * 0.08)
        for metric, value in result.benchmark_predictions.items():
            interval = self._metric_interval(metric, value, uncertainty)
            predictions.append(
                BenchmarkPrediction(
                    metric=metric,
                    expected_value=value,
                    lower_bound=interval[0],
                    upper_bound=interval[1],
                    confidence=result.confidence,
                    rationale=self._rationale(metric, result),
                )
            )
        return predictions

    def rank_candidates(self, results: Iterable[SimulationResult]) -> list[SimulationResult]:
        """Rank simulations by predicted quality, confidence, cost, and risk."""

        return sorted(results, key=self._ranking_score, reverse=True)

    def compare_to_baseline(
        self,
        result: SimulationResult,
        baseline_metrics: Mapping[str, float],
    ) -> dict[str, float]:
        """Return predicted metric deltas against a supplied baseline."""

        return {
            metric: round(predicted - baseline_metrics.get(metric, predicted), 4)
            for metric, predicted in result.benchmark_predictions.items()
        }

    def portfolio_summary(self, results: Iterable[SimulationResult]) -> dict[str, float]:
        """Summarize a batch of simulated experiments for planning reviews."""

        materialized = list(results)
        if not materialized:
            return {
                "candidate_count": 0,
                "mean_quality_score": 0.0,
                "mean_cost_usd": 0.0,
                "quality_stddev": 0.0,
                "highest_risk": 0.0,
            }
        quality_scores = [result.quality_score for result in materialized]
        costs = [result.estimated_cost_usd for result in materialized]
        risks = [result.implementation_risk for result in materialized]
        return {
            "candidate_count": float(len(materialized)),
            "mean_quality_score": round(mean(quality_scores), 4),
            "mean_cost_usd": round(mean(costs), 2),
            "quality_stddev": round(pstdev(quality_scores), 4),
            "highest_risk": round(max(risks), 4),
        }

    def _ranking_score(self, result: SimulationResult) -> float:
        cost_penalty = min(0.30, result.estimated_cost_usd / 100_000)
        risk_penalty = result.implementation_risk * 0.35
        confidence_bonus = result.confidence * 0.18
        quality_term = result.quality_score / 100
        return quality_term + confidence_bonus - risk_penalty - cost_penalty

    def _metric_interval(self, metric: str, value: float, uncertainty: float) -> tuple[float, float]:
        if metric.endswith("_ms"):
            lower = value * (1 - uncertainty)
            upper = value * (1 + uncertainty * 1.4)
            return round(max(0.0, lower), 4), round(upper, 4)
        if value <= 1:
            return round(max(0.0, value - uncertainty), 4), round(min(1.0, value + uncertainty), 4)
        return round(max(0.0, value - uncertainty * 100), 4), round(min(100.0, value + uncertainty * 100), 4)

    def _rationale(self, metric: str, result: SimulationResult) -> str:
        top_ablation = max(result.ablation_impacts, key=result.ablation_impacts.get, default="none")
        return (
            f"{metric} forecast from {result.architecture_name}/{result.experiment_name}; "
            f"confidence={result.confidence:.2f}, risk={result.implementation_risk:.2f}, "
            f"strongest ablation signal={top_ablation}."
        )
