"""Command-line entry point for a default V15 simulation workflow."""

from __future__ import annotations

import json
from dataclasses import asdict

from .simulation_engine import ArchitectureSpec, ExperimentSpec
from .workflows import ExperimentPlanningWorkflow


def main() -> None:
    """Run a sample V15 experiment plan and print JSON for automation."""

    architectures = [
        ArchitectureSpec(
            name="retrieval-grounded-transformer",
            encoder_layers=12,
            decoder_layers=12,
            hidden_size=768,
            retrieval_depth=8,
            context_window=16_384,
            novelty_factor=0.45,
        ),
        ArchitectureSpec(
            name="long-context-distilled-transformer",
            encoder_layers=16,
            decoder_layers=8,
            hidden_size=1_024,
            retrieval_depth=4,
            context_window=32_768,
            quantization_bits=8,
            parameter_count_millions=420,
            novelty_factor=0.62,
        ),
    ]
    experiment = ExperimentSpec(
        name="v15-preimplementation-study",
        dataset_size=120_000,
        training_steps=12_000,
        evaluation_samples=5_000,
        ablations=("retrieval", "reranking", "citation_grounding"),
    )
    plan = ExperimentPlanningWorkflow().generate_plan(
        objective="Predict research outcomes for arXiv paper summarisation before implementation.",
        architectures=architectures,
        experiment=experiment,
    )
    print(json.dumps(asdict(plan), indent=2))


if __name__ == "__main__":
    main()
