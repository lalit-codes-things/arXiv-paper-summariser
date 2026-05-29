"""Command line interface for the V9 implementation workflow platform."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .workflow import V9Workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert paper text into a V9 implementation workflow.")
    parser.add_argument("paper", type=Path, help="Path to a plain-text research paper or extracted PDF text.")
    parser.add_argument("--output-dir", type=Path, help="Directory for generated starter repository files.")
    parser.add_argument("--json", action="store_true", help="Print a JSON summary instead of markdown.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paper_text = args.paper.read_text(encoding="utf-8")
    workflow = V9Workflow()
    result = workflow.write_starter_repo(paper_text, args.output_dir) if args.output_dir else workflow.run(paper_text)
    if args.json:
        print(
            json.dumps(
                {
                    "pseudo_code_blocks": len(result.pseudo_code),
                    "architecture_components": [component.name for component in result.architecture.components],
                    "dependencies": result.dependencies.python_packages,
                    "experiments": [experiment.name for experiment in result.experiments],
                    "starter_repo_files": [file.path for file in result.starter_repo],
                },
                indent=2,
            )
        )
    else:
        print(result.checklist_markdown)
        print(result.experiment_config_yaml)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
