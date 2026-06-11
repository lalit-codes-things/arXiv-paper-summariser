from __future__ import annotations

from datetime import datetime, timedelta, timezone

from arxiv_research_copilot_v4 import GraphSchema, InMemoryResearchGraph, PaperRanker, build_default_orchestrator
from arxiv_research_copilot_v4.comparison import PaperComparisonEngine
from arxiv_research_copilot_v4.roadmap import RoadmapGenerator
from arxiv_research_copilot_v4.scheduler import DailyScheduler
from arxiv_research_copilot_v4.monitoring import DailyMonitoringWorkflow, JsonDigestSink


class StubArxivClient:
    def fetch_recent(self, categories, max_results=50):
        return sample_papers()[:max_results]


def sample_papers():
    now = datetime.now(timezone.utc)
    return [
        paper(
            "2401.00001",
            "Agentic RAG for Scientific Discovery",
            "We propose an agentic retrieval augmented architecture with graph memory and citation grounding. Experiments on QA benchmarks outperform strong baselines with open-source code.",
            now,
        ),
        paper(
            "2401.00002",
            "Graph Memory for Research Agents",
            "This paper presents graph memory for language agents. Benchmark evaluation studies retrieval planning, citation grounding, and limitations in long-horizon scientific workflows.",
            now - timedelta(days=1),
        ),
    ]


def paper(paper_id, title, abstract, published):
    return __import__("arxiv_research_copilot_v4.models", fromlist=["Paper"]).Paper(
        paper_id=paper_id,
        title=title,
        abstract=abstract,
        authors=["Ada Lovelace", "Grace Hopper"],
        categories=["cs.AI", "cs.CL"],
        published=published,
        primary_category="cs.AI",
        url=f"https://arxiv.org/abs/{paper_id}",
    )


def test_default_orchestrator_runs_all_agents_and_graph_memory():
    papers = sample_papers()
    orchestrator = build_default_orchestrator()

    result = orchestrator.run_research_workflow(papers)

    assert len(result.agent_results) == 16
    assert result.graph_stats["papers"] == 2
    assert result.trends
    assert result.comparisons[0].paper_ids == ["2401.00001", "2401.00002"]


def test_graph_schema_and_related_papers():
    graph = InMemoryResearchGraph()
    for item in sample_papers():
        graph.ingest_paper(item)

    assert graph.related_papers("2401.00001") == ["2401.00002"]
    assert "CREATE CONSTRAINT paper_id" in GraphSchema().constraints()[0]
    assert "MERGE (p:Paper" in GraphSchema().paper_upsert_cypher()


def test_ranker_prefers_recent_evaluated_open_source_paper():
    papers = sample_papers()
    ranked = PaperRanker().rank(papers)

    assert ranked[0][0].paper_id == "2401.00001"
    assert ranked[0][1] > ranked[1][1]


def test_roadmap_and_comparison_engine():
    papers = sample_papers()

    roadmap = RoadmapGenerator().generate("How to learn research agents", papers)
    comparison = PaperComparisonEngine().compare(papers)

    assert roadmap[0].title == "Orientation"
    assert "methods" in comparison.dimensions["2401.00001"]


def test_daily_monitoring_workflow_with_stub_client(tmp_path):
    workflow = DailyMonitoringWorkflow(arxiv_client=StubArxivClient(), sink=JsonDigestSink(tmp_path))

    digest = workflow.run(max_results=2, top_n=1)

    assert len(digest.top_papers) == 1
    assert (tmp_path / f"{digest.date.date().isoformat()}-ai-research-digest.json").exists()


def test_scheduler_next_run_moves_to_tomorrow_after_run_time():
    workflow = DailyMonitoringWorkflow(arxiv_client=StubArxivClient())
    scheduler = DailyScheduler(workflow)
    now = datetime(2026, 5, 28, 9, 0, tzinfo=timezone.utc)

    assert scheduler.next_run_after(now).date().isoformat() == "2026-05-29"
