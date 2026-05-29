# arXiv Paper Summariser V9

V9 upgrades the project from summarisation into an implementation-workflow platform. It converts research paper text into executable engineering assets: pseudo-code, architecture reconstruction, implementation plans, PyTorch skeletons, experiment configurations, reproducibility workflows, and starter repositories.

## Capabilities

- **Pseudo-code extraction** from explicit algorithms or inferred method prose.
- **Architecture reconstruction** into components, evidence, and data-flow edges.
- **Dependency detection** for Python packages, datasets, metrics, hardware, and tools.
- **Implementation planning** with prioritized tasks and deliverables.
- **PyTorch skeleton generation** for model, data, procedure, and training modules.
- **Experiment generation** for baseline reproduction, seed sweeps, and ablations.
- **Reproducibility analysis** for seeds, hyperparameters, splits, hardware, code, and lockfiles.
- **Starter repo output** with checklists, configs, requirements, and training pipeline stubs.

## Quick start

```bash
python -m pip install -e .
arxiv-v9 paper.txt --output-dir generated/starter-repo
```

To print a compact machine-readable summary instead of markdown:

```bash
arxiv-v9 paper.txt --json
```

## Python API

```python
from arxiv_paper_summariser.v9 import V9Workflow

paper_text = """
Algorithm 1: Train the encoder
1. Initialize the transformer encoder.
2. Train with Adam on CIFAR-10 and report accuracy.
"""

result = V9Workflow().run(paper_text)
print(result.checklist_markdown)
print([file.path for file in result.starter_repo])
```

## Generated outputs

`V9Workflow.run()` returns a `V9WorkflowResult` containing:

- `pseudo_code`: normalized algorithm blocks.
- `architecture`: reconstructed components and edges.
- `dependencies`: packages, datasets, metrics, hardware, and tools.
- `implementation_plan`: concrete implementation tasks.
- `experiments`: experiment specifications.
- `reproducibility`: findings and mitigations.
- `starter_repo`: generated files for a new implementation repository.
- `checklist_markdown`: implementation checklist markdown.
- `experiment_config_yaml`: experiment configuration YAML.
- `training_pipeline`: high-level executable training workflow.

## Development

```bash
python -m pytest
```
