# arXiv Paper Summariser — V15 Research Simulation Platform

V15 upgrades this repository from a placeholder into a pre-implementation research
simulation toolkit. The platform helps teams estimate likely experiment outcomes
before committing engineering effort or cloud budget.

## V15 capabilities

- **Architecture simulation**: score candidate summarisation architectures for
  expected quality, implementation risk, complexity, and throughput.
- **Experiment estimation**: estimate GPU hours, cloud spend, engineering effort,
  storage cost, and confidence for planned research runs.
- **Compute cost prediction**: model GPU pricing across common accelerator types
  and include engineering review effort in total cost.
- **Ablation simulation**: predict component-level impact for retrieval,
  reranking, compression, long-context, distillation, and citation-grounding work.
- **Expected benchmark prediction**: forecast ROUGE-L, faithfulness, citation F1,
  and latency with confidence intervals.
- **Experiment planning workflows**: turn simulation outputs into acceptance gates,
  fallback plans, and an implementation backlog.

## Quick start

```bash
python -m arxiv_paper_summariser_v15.cli
```

or, after installation:

```bash
arxiv-v15-simulate
```

## Example

```python
from arxiv_paper_summariser_v15 import (
    ArchitectureSpec,
    ExperimentPlanningWorkflow,
    ExperimentSpec,
)

architectures = [
    ArchitectureSpec(
        name="retrieval-grounded-transformer",
        encoder_layers=12,
        decoder_layers=12,
        hidden_size=768,
        retrieval_depth=8,
        context_window=16_384,
    )
]
experiment = ExperimentSpec(
    name="v15-preimplementation-study",
    dataset_size=120_000,
    training_steps=12_000,
    evaluation_samples=5_000,
)

plan = ExperimentPlanningWorkflow().generate_plan(
    objective="Predict research outcomes before implementation.",
    architectures=architectures,
    experiment=experiment,
)

print(plan.selected_candidate.recommendation)
```

## Module map

- `arxiv_paper_summariser_v15.simulation_engine` contains the simulation engine,
  architecture specifications, experiment specifications, compute profiles, and
  simulation result model.
- `arxiv_paper_summariser_v15.benchmark_prediction` converts simulation results
  into benchmark confidence intervals, baseline deltas, rankings, and portfolio
  summaries.
- `arxiv_paper_summariser_v15.workflows` generates experiment plans with research
  steps, acceptance gates, fallback plans, and implementation backlog items.
- `arxiv_paper_summariser_v15.cli` runs a default V15 simulation workflow and
  emits JSON for automation.

## Development

```bash
python -m pytest
python -m arxiv_paper_summariser_v15.cli
```
