"""Equation interpretation and reasoning workflows."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .modalities import Modality, PaperAsset, UnderstandingResult
from .ocr import OCRPipeline


@dataclass
class EquationReasoningWorkflow:
    """Interprets symbolic expressions found in papers."""

    ocr: OCRPipeline

    def run(self, asset: PaperAsset) -> UnderstandingResult:
        expression = self._extract_expression(asset)
        ocr_result = self.ocr.run(asset)
        if not expression:
            expression = ocr_result.extracted.get("text", "")

        variables = sorted(set(re.findall(r"\b[a-zA-Z](?:_[a-zA-Z0-9]+)?\b", expression)))
        operators = re.findall(r"[=+\-*/^∑∫≤≥≈≠]", expression)
        reasoning_steps = self._reason_about(expression, variables, operators)
        confidence = 0.9 if expression else 0.15

        return UnderstandingResult(
            asset_id=asset.asset_id,
            modality=Modality.EQUATION,
            summary=reasoning_steps[0] if reasoning_steps else "No equation could be interpreted.",
            evidence=reasoning_steps,
            extracted={
                "expression": expression,
                "variables": variables,
                "operators": operators,
                "ocr": ocr_result.extracted,
            },
            confidence=confidence,
            warnings=[] if expression else ["Equation text was unavailable."],
        )

    @staticmethod
    def _extract_expression(asset: PaperAsset) -> str:
        for key in ("latex", "mathml", "equation", "ocr_text"):
            value = asset.metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return asset.content.strip() if isinstance(asset.content, str) else ""

    @staticmethod
    def _reason_about(expression: str, variables: list[str], operators: list[str]) -> list[str]:
        if not expression:
            return []
        steps = [f"Interpreted expression `{expression}` with {len(variables)} variable(s)."]
        if "=" in operators:
            lhs, _, rhs = expression.partition("=")
            steps.append(f"The equation relates `{lhs.strip()}` to `{rhs.strip()}`.")
        if "∑" in operators or "sum" in expression.lower():
            steps.append("The expression includes aggregation, so downstream summaries should describe the indexed quantity being accumulated.")
        if "∫" in operators or "int" in expression.lower():
            steps.append("The expression includes integration, suggesting a continuous accumulation or expectation over a domain.")
        if any(op in operators for op in ("≤", "≥", "≈", "≠")):
            steps.append("The expression uses comparison/approximation semantics that should be preserved in natural-language explanations.")
        return steps
