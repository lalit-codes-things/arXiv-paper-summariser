"""Pseudo-code and algorithm extraction for V9."""

from __future__ import annotations

import re

from .models import PseudoCodeBlock
from .text import sentences, unique_preserve_order

_ALGORITHM_BLOCK_RE = re.compile(
    r"(?P<title>(?:Algorithm|Procedure|Method)\s*\d*[:. -]*[^\n]*)\n(?P<body>.*?)(?=\n\s*(?:Algorithm|Procedure|Method)\s*\d*[:. -]|\n\s*(?:\d+\.?\s*)?[A-Z][A-Za-z /-]{2,60}\n|\Z)",
    re.IGNORECASE | re.DOTALL,
)
_STEP_RE = re.compile(r"^(?:\d+[.)]|[-*•]|Input:|Output:|Initialize|For |While |Repeat|Return|If |Else)", re.IGNORECASE)
_ACTION_WORDS = (
    "initialize",
    "sample",
    "encode",
    "decode",
    "optimize",
    "train",
    "update",
    "compute",
    "normalize",
    "rank",
    "generate",
    "predict",
    "evaluate",
)


class PseudoCodeExtractor:
    """Extract implementation-ready algorithm steps from paper prose."""

    def extract(self, paper_text: str) -> list[PseudoCodeBlock]:
        """Return explicit algorithms plus inferred pseudo-code from method prose."""

        blocks = self._explicit_blocks(paper_text)
        if blocks:
            return blocks
        return self._inferred_blocks(paper_text)

    def _explicit_blocks(self, paper_text: str) -> list[PseudoCodeBlock]:
        blocks: list[PseudoCodeBlock] = []
        for match in _ALGORITHM_BLOCK_RE.finditer(paper_text):
            title = match.group("title").strip() or "Algorithm"
            raw_lines = [line.strip() for line in match.group("body").splitlines()]
            steps = [self._clean_step(line) for line in raw_lines if self._looks_like_step(line)]
            if steps:
                blocks.append(PseudoCodeBlock(title=title, steps=unique_preserve_order(steps), source_heading=title))
        return blocks

    def _inferred_blocks(self, paper_text: str) -> list[PseudoCodeBlock]:
        candidate_steps = []
        for sentence in sentences(paper_text):
            lower = sentence.lower()
            if any(word in lower for word in _ACTION_WORDS):
                candidate_steps.append(self._clean_step(sentence))
        if not candidate_steps:
            candidate_steps = [
                "Load and validate the paper dataset.",
                "Instantiate the reconstructed architecture.",
                "Train the model with the reported objective.",
                "Evaluate reported metrics and save artifacts.",
            ]
        return [PseudoCodeBlock(title="Inferred implementation procedure", steps=unique_preserve_order(candidate_steps[:12]))]

    @staticmethod
    def _looks_like_step(line: str) -> bool:
        return bool(line and (_STEP_RE.search(line) or any(word in line.lower() for word in _ACTION_WORDS)))

    @staticmethod
    def _clean_step(line: str) -> str:
        line = re.sub(r"^\s*(?:\d+[.)]|[-*•])\s*", "", line.strip())
        line = re.sub(r"\s+", " ", line)
        return line.rstrip(";") + ("" if line.endswith(".") else ".")
