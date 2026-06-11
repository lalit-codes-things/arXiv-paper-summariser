"""Command line interface."""

from __future__ import annotations

import argparse
import json

from arxiv_copilot.pipeline import default_pipeline
from arxiv_copilot.utils.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Arxiv Research Copilot V2")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--arxiv-id", action="append", help="Process one arXiv ID; repeat for batch processing")
    group.add_argument("--category", help="Process newest papers from an arXiv category, e.g. cs.AI")
    group.add_argument("--newest-ai", action="store_true", help="Process newest cs.AI papers")
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--no-pdf", action="store_true", help="Use abstracts only instead of downloading PDFs")
    parser.add_argument("--no-semantic-scholar", action="store_true", help="Disable Semantic Scholar enrichment")
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    args = build_parser().parse_args(argv)
    pipeline = default_pipeline(args.data_dir)
    pipeline.config.download_pdfs = not args.no_pdf
    pipeline.config.enrich_semantic_scholar = not args.no_semantic_scholar

    if args.arxiv_id:
        results = pipeline.process_many(args.arxiv_id)
    elif args.category:
        results = pipeline.process_category(args.category, max_results=args.max_results)
    else:
        results = pipeline.process_newest_ai(max_results=args.max_results)

    print(json.dumps([result.to_dict() for result in results], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
