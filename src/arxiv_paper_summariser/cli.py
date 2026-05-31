"""Command line entry point for V8 literature review workflows."""

from __future__ import annotations

import argparse

from .models import CitationStyle, ReviewConfig
from .workflows import ReviewGenerationWorkflow


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a V8 structured literature review from paper JSON.")
    parser.add_argument("input", help="Path to a JSON list of paper records")
    parser.add_argument("output", help="Path for the generated Markdown review")
    parser.add_argument("--title", default="Structured Literature Review", help="Review title")
    parser.add_argument("--citation-style", choices=[style.value for style in CitationStyle], default=CitationStyle.APA.value)
    args = parser.parse_args()

    config = ReviewConfig(title=args.title, citation_style=CitationStyle(args.citation_style))
    workflow = ReviewGenerationWorkflow()
    review = workflow.from_json(args.input, config=config)
    workflow.export_markdown(review, args.output)
