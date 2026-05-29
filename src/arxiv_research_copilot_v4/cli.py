"""Command-line interface for Arxiv Research Copilot V4."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json

from .digest import DigestRenderer
from .models import Paper
from .monitoring import DEFAULT_CATEGORIES, DailyMonitoringWorkflow, JsonDigestSink
from .orchestration import build_default_orchestrator
from .roadmap import RoadmapGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Arxiv Research Copilot V4 autonomous research agent ecosystem")
    subparsers = parser.add_subparsers(dest="command", required=True)

    monitor = subparsers.add_parser("monitor", help="Run daily monitoring once")
    monitor.add_argument("--max-results", type=int, default=25)
    monitor.add_argument("--top-n", type=int, default=10)
    monitor.add_argument("--output-dir", default="digests")

    demo = subparsers.add_parser("demo", help="Run the multi-agent workflow on a sample paper")
    demo.add_argument("--json", action="store_true")

    roadmap = subparsers.add_parser("roadmap", help="Generate a roadmap from a sample corpus")
    roadmap.add_argument("objective")

    args = parser.parse_args()
    if args.command == "monitor":
        workflow = DailyMonitoringWorkflow(sink=JsonDigestSink(args.output_dir))
        digest = workflow.run(categories=DEFAULT_CATEGORIES, max_results=args.max_results, top_n=args.top_n)
        print(DigestRenderer().to_markdown(digest))
    elif args.command == "demo":
        paper = _sample_paper()
        result = build_default_orchestrator().run_research_workflow([paper], compare=False)
        print(json.dumps(asdict(result), default=str, indent=2) if args.json else result)
    elif args.command == "roadmap":
        paper = _sample_paper()
        steps = RoadmapGenerator().generate(args.objective, [paper])
        print(json.dumps([asdict(step) for step in steps], indent=2))


def _sample_paper() -> Paper:
    return Paper(
        paper_id="2401.00001",
        title="Agentic Retrieval-Augmented Reasoning for Scientific Discovery",
        abstract="We propose an agentic retrieval augmented architecture for scientific discovery. The system uses tool-using language agents, graph memory, and benchmark evaluation to improve multi-hop research question answering. Experiments outperform strong baselines and include ablations for retrieval, planning, and citation grounding.",
        authors=["Ada Lovelace", "Grace Hopper"],
        categories=["cs.AI", "cs.CL"],
        published=datetime.now(timezone.utc),
        primary_category="cs.AI",
        url="https://arxiv.org/abs/2401.00001",
    )


if __name__ == "__main__":
    main()
