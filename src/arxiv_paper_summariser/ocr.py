"""OCR pipeline primitives for research-paper assets."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol

from .modalities import Modality, PaperAsset, UnderstandingResult


class TextRecognizer(Protocol):
    """Protocol implemented by OCR backends."""

    def recognize(self, asset: PaperAsset) -> str:
        """Return text recognized from an asset."""


@dataclass
class MetadataTextRecognizer:
    """Deterministic OCR fallback that reads text supplied in asset metadata/content."""

    metadata_keys: tuple[str, ...] = ("ocr_text", "alt_text", "raw_text")

    def recognize(self, asset: PaperAsset) -> str:
        for key in self.metadata_keys:
            value = asset.metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        if isinstance(asset.content, str):
            return asset.content.strip()
        return ""


@dataclass
class OCRPipeline:
    """Runs OCR, cleanup, and structural token extraction for paper visuals."""

    recognizer: TextRecognizer = field(default_factory=MetadataTextRecognizer)

    def run(self, asset: PaperAsset) -> UnderstandingResult:
        text = self._normalize(self.recognizer.recognize(asset))
        tokens = self._extract_structural_tokens(text)
        warnings = [] if text else ["No OCR text was available from the configured recognizer."]
        return UnderstandingResult(
            asset_id=asset.asset_id,
            modality=Modality.OCR,
            summary=self._summarize(text, tokens),
            evidence=[text] if text else [],
            extracted={"text": text, "tokens": tokens},
            confidence=0.85 if text else 0.1,
            warnings=warnings,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _extract_structural_tokens(text: str) -> dict[str, list[str]]:
        return {
            "numbers": re.findall(r"(?<!\w)[+-]?(?:\d+\.\d+|\d+)(?:e[+-]?\d+)?", text, flags=re.I),
            "variables": re.findall(r"\b[a-zA-Z](?:_[a-zA-Z0-9]+)?\b", text),
            "operators": re.findall(r"[=+\-*/∑∫≤≥≈≠]", text),
        }

    @staticmethod
    def _summarize(text: str, tokens: dict[str, list[str]]) -> str:
        if not text:
            return "OCR found no readable text."
        return (
            "OCR extracted readable text with "
            f"{len(tokens['numbers'])} numeric token(s), "
            f"{len(tokens['variables'])} variable-like token(s), and "
            f"{len(tokens['operators'])} operator token(s)."
        )
