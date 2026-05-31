"""Dependency detection for implementation planning."""

from __future__ import annotations

import re

from .models import DependencyReport
from .text import unique_preserve_order

_PACKAGE_PATTERNS = {
    "torch": r"\b(?:pytorch|torch)\b",
    "torchvision": r"\btorchvision\b",
    "transformers": r"\b(?:transformers|hugging\s*face|bert|gpt|llama)\b",
    "numpy": r"\bnumpy\b",
    "scikit-learn": r"\b(?:scikit-learn|sklearn)\b",
    "pandas": r"\bpandas\b",
    "opencv-python": r"\b(?:opencv|cv2)\b",
    "networkx": r"\bnetworkx\b",
    "hydra-core": r"\bhydra\b",
    "wandb": r"\b(?:wandb|weights\s*&\s*biases)\b",
}
_DATASET_PATTERNS = [
    "ImageNet",
    "CIFAR-10",
    "CIFAR-100",
    "COCO",
    "MNIST",
    "Fashion-MNIST",
    "GLUE",
    "SQuAD",
    "WikiText-103",
    "LibriSpeech",
    "MIMIC-III",
]
_HARDWARE_RE = re.compile(r"\b(?:A100|V100|H100|TPU(?:v\d+)?|GPU|CUDA|NVIDIA|8\s*x\s*GPU|multi-gpu)\b", re.IGNORECASE)
_METRIC_PATTERNS = ["accuracy", "F1", "AUROC", "BLEU", "ROUGE", "perplexity", "mAP", "IoU", "RMSE", "MAE", "loss"]
_TOOL_PATTERNS = ["Docker", "Conda", "Slurm", "Ray", "DVC", "MLflow", "TensorBoard"]


class DependencyDetector:
    """Detect code, data, metric, hardware, and tooling requirements."""

    def detect(self, paper_text: str) -> DependencyReport:
        text = paper_text.lower()
        packages = [pkg for pkg, pattern in _PACKAGE_PATTERNS.items() if re.search(pattern, text, re.IGNORECASE)]
        if not packages and any(token in text for token in ("neural", "network", "gradient", "backprop")):
            packages.append("torch")
        datasets = [name for name in _DATASET_PATTERNS if re.search(rf"\b{re.escape(name)}\b", paper_text, re.IGNORECASE)]
        hardware = _HARDWARE_RE.findall(paper_text)
        metrics = [name for name in _METRIC_PATTERNS if re.search(rf"\b{re.escape(name)}\b", paper_text, re.IGNORECASE)]
        tools = [name for name in _TOOL_PATTERNS if re.search(rf"\b{re.escape(name)}\b", paper_text, re.IGNORECASE)]
        return DependencyReport(
            python_packages=unique_preserve_order(packages or ["torch", "numpy"]),
            datasets=unique_preserve_order(datasets or ["paper_dataset"]),
            hardware=unique_preserve_order([item.upper() if item.lower() == "gpu" else item for item in hardware] or ["single GPU or CPU fallback"]),
            metrics=unique_preserve_order(metrics or ["loss"]),
            external_tools=unique_preserve_order(tools or ["Docker"]),
        )
