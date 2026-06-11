"""Architecture reconstruction from research paper text."""

from __future__ import annotations

import re

from .models import ArchitectureComponent, ArchitectureGraph, PseudoCodeBlock
from .text import sentences, slugify, unique_preserve_order

_COMPONENT_KEYWORDS = {
    "encoder": "module",
    "decoder": "module",
    "attention": "module",
    "transformer": "backbone",
    "cnn": "backbone",
    "convolution": "module",
    "mlp": "head",
    "classifier": "head",
    "embedding": "module",
    "normalization": "module",
    "loss": "objective",
    "optimizer": "training",
    "scheduler": "training",
    "dataset": "data",
    "dataloader": "data",
    "augmentation": "data",
}


class ArchitectureParser:
    """Infer an implementation graph and module boundaries."""

    def parse(self, paper_text: str, pseudo_code: list[PseudoCodeBlock]) -> ArchitectureGraph:
        components = self._components_from_text(paper_text)
        if not components:
            components = self._fallback_components(pseudo_code)
        edges = self._infer_edges(components)
        return ArchitectureGraph(components=components, edges=edges)

    def _components_from_text(self, paper_text: str) -> list[ArchitectureComponent]:
        found: list[ArchitectureComponent] = []
        for sentence in sentences(paper_text):
            lower = sentence.lower()
            for keyword, kind in _COMPONENT_KEYWORDS.items():
                if keyword in lower:
                    name = self._component_name(keyword, sentence)
                    found.append(
                        ArchitectureComponent(
                            name=name,
                            kind=kind,
                            evidence=sentence,
                            inputs=self._extract_io(sentence, "input"),
                            outputs=self._extract_io(sentence, "output"),
                        )
                    )
        deduped: dict[str, ArchitectureComponent] = {}
        for component in found:
            deduped.setdefault(slugify(component.name), component)
        return list(deduped.values())[:16]

    @staticmethod
    def _component_name(keyword: str, sentence: str) -> str:
        pattern = re.compile(rf"(?:the|a|an|our)?\s*([A-Z]?[a-zA-Z0-9_-]*\s*{keyword}\s*(?:layer|module|block|head|network)?)", re.IGNORECASE)
        match = pattern.search(sentence)
        if match:
            return " ".join(match.group(1).split()).title()
        return keyword.title()

    @staticmethod
    def _extract_io(sentence: str, label: str) -> list[str]:
        match = re.search(rf"{label}s?\s+(?:are|is|of|to)?\s*([^.;:,]+)", sentence, re.IGNORECASE)
        if not match:
            return []
        return [part.strip() for part in re.split(r"\band\b|,", match.group(1)) if part.strip()][:3]

    @staticmethod
    def _fallback_components(pseudo_code: list[PseudoCodeBlock]) -> list[ArchitectureComponent]:
        evidence = " ".join(step for block in pseudo_code for step in block.steps[:2])
        return [
            ArchitectureComponent("Dataset Loader", "data", evidence),
            ArchitectureComponent("Paper Model", "backbone", evidence),
            ArchitectureComponent("Training Objective", "objective", evidence),
            ArchitectureComponent("Evaluator", "evaluation", evidence),
        ]

    @staticmethod
    def _infer_edges(components: list[ArchitectureComponent]) -> list[tuple[str, str, str]]:
        order = ["data", "module", "backbone", "head", "objective", "training", "evaluation"]
        sorted_components = sorted(enumerate(components), key=lambda item: (order.index(item[1].kind) if item[1].kind in order else 99, item[0]))
        names = unique_preserve_order([component.name for _, component in sorted_components])
        return [(source, target, "feeds") for source, target in zip(names, names[1:])]
