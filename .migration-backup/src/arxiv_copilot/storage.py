"""Local JSON result storage."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arxiv_copilot.schemas import PaperResult


@dataclass(slots=True)
class JSONStorage:
    root: Path = Path("data/results")

    def save(self, result: PaperResult) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / f"{_safe_name(result.paper.arxiv_id)}.json"
        path.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def load(self, arxiv_id: str) -> dict[str, Any]:
        path = self.root / f"{_safe_name(arxiv_id)}.json"
        return json.loads(path.read_text(encoding="utf-8"))


def _safe_name(value: str) -> str:
    return value.replace("/", "_").replace(":", "_")
