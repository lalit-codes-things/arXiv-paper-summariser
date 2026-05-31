"""Reproducibility workflow generation and risk analysis."""

from __future__ import annotations

import re

from .models import DependencyReport, ReproducibilityFinding


class ReproducibilityAnalyzer:
    """Assess paper text for reproducibility support and missing details."""

    CHECKS = {
        "random seeds": r"\bseed(?:s|ed)?\b|random state",
        "hyperparameters": r"learning rate|batch size|epoch|optimizer|weight decay",
        "data splits": r"train(?:ing)? split|validation split|test split|cross-validation",
        "hardware": r"gpu|tpu|cuda|a100|v100|h100",
        "source code": r"github|code is available|repository|supplementary code",
    }

    def analyze(self, paper_text: str, dependencies: DependencyReport) -> list[ReproducibilityFinding]:
        findings: list[ReproducibilityFinding] = []
        for category, pattern in self.CHECKS.items():
            present = bool(re.search(pattern, paper_text, re.IGNORECASE))
            findings.append(
                ReproducibilityFinding(
                    category=category,
                    status="present" if present else "missing",
                    detail=f"Detected {category} information." if present else f"No explicit {category} details were detected.",
                    mitigation="Capture in configs and README before reproduction runs." if present else f"Add an explicit {category} section to the implementation notes.",
                )
            )
        findings.append(
            ReproducibilityFinding(
                category="dependency lockfile",
                status="required",
                detail=f"Detected packages: {', '.join(dependencies.python_packages)}.",
                mitigation="Generate requirements.txt and record package versions after environment solve.",
            )
        )
        return findings

    @staticmethod
    def workflow_markdown(findings: list[ReproducibilityFinding]) -> str:
        lines = ["# Reproducibility Workflow", "", "1. Pin dependencies and record hardware metadata."]
        lines.extend(
            [
                "2. Run baseline reproduction with a fixed seed.",
                "3. Run seed sweep and report mean/std for primary metrics.",
                "4. Run ablations that isolate reconstructed architecture components.",
                "5. Store configs, logs, checkpoints, and generated tables as immutable artifacts.",
                "",
                "## Findings",
            ]
        )
        for finding in findings:
            lines.append(f"- **{finding.category}** [{finding.status}]: {finding.detail} Mitigation: {finding.mitigation}")
        return "\n".join(lines) + "\n"
