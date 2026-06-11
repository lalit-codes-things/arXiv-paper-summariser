from pathlib import Path

from arxiv_paper_summariser.v9 import V9Workflow


PAPER_TEXT = """
Method
Our transformer encoder uses an attention module and an MLP classifier. The input is CIFAR-10 images and the output is class probabilities.
Algorithm 1: Training procedure
1. Initialize the transformer encoder and classifier.
2. Train with PyTorch using Adam for 10 epochs with batch size 32.
3. Evaluate accuracy on the test split and save checkpoints.
We use a random seed, an NVIDIA A100 GPU, Docker, and report accuracy.
"""


def test_v9_workflow_generates_implementation_assets():
    result = V9Workflow().run(PAPER_TEXT)

    assert result.pseudo_code[0].steps
    assert any(component.kind == "backbone" for component in result.architecture.components)
    assert "torch" in result.dependencies.python_packages
    assert "CIFAR-10" in result.dependencies.datasets
    assert any(task.title.startswith("Implement") for task in result.implementation_plan)
    assert {experiment.name for experiment in result.experiments} == {
        "baseline_reproduction",
        "seed_sweep",
        "core_ablation",
    }
    assert "Implementation Checklist" in result.checklist_markdown
    assert "experiments:" in result.experiment_config_yaml
    assert "build_model" in result.training_pipeline
    assert "src/paper_model/model.py" in {file.path for file in result.starter_repo}


def test_write_starter_repo_materializes_files(tmp_path: Path):
    result = V9Workflow().write_starter_repo(PAPER_TEXT, tmp_path)

    expected_paths = {file.path for file in result.starter_repo}
    assert "scripts/train.py" in expected_paths
    assert (tmp_path / "scripts" / "train.py").exists()
    assert (tmp_path / "docs" / "implementation_checklist.md").read_text(encoding="utf-8").startswith("# Implementation Checklist")
