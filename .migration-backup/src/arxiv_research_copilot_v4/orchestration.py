"""Agent orchestration layer with a LangGraph-ready state machine fallback."""

from __future__ import annotations

import importlib.util
from collections.abc import Sequence
from typing import Any

from .agents import (
    AgentContext,
    CitationAgent,
    FlashcardAgent,
    MethodologyAgent,
    PaperComparisonAgent,
    ResearchAgent,
    ResearchRoadmapAgent,
    SummarizerAgent,
    TrendAnalysisAgent,
    WeaknessDetectorAgent,
)
from .knowledge_graph import InMemoryResearchGraph
from .models import AgentResult, Paper, WorkflowResult
from .trend_detection import TrendDetector


class AgentOrchestrator:
    """Coordinates V4 agents, graph memory, comparisons, trends, and roadmaps."""

    def __init__(self, agents: Sequence[ResearchAgent], *, graph_memory: InMemoryResearchGraph | None = None) -> None:
        self.agents = list(agents)
        self.graph_memory = graph_memory or InMemoryResearchGraph()
        self.trend_detector = TrendDetector()
        self.comparison_agent = next((agent for agent in self.agents if isinstance(agent, PaperComparisonAgent)), PaperComparisonAgent())

    def run_paper_pipeline(self, paper: Paper, *, cohort: list[Paper] | None = None, objective: str | None = None) -> list[AgentResult]:
        """Run all agents on one paper and update graph memory."""

        if paper.paper_id not in self.graph_memory.papers:
            self.graph_memory.ingest_paper(paper)
        papers = cohort or list(self.graph_memory.papers.values())
        results: list[AgentResult] = []
        context = AgentContext(papers=papers, previous_results=results, graph_memory=self.graph_memory, objective=objective)
        for agent in self.agents:
            result = agent.run(paper, context)
            results.append(result)
        return results

    def run_research_workflow(self, papers: list[Paper], *, objective: str | None = None, compare: bool = True) -> WorkflowResult:
        """Run the full autonomous research workflow for a cohort of papers."""

        for paper in papers:
            self.graph_memory.ingest_paper(paper)
        agent_results: list[AgentResult] = []
        for paper in papers:
            agent_results.extend(self.run_paper_pipeline(paper, cohort=papers, objective=objective))
        trends = self.trend_detector.detect(papers)
        comparisons = [self.comparison_agent.compare(papers)] if compare and len(papers) > 1 else []
        roadmap = []
        roadmap_agent = next((agent for agent in self.agents if isinstance(agent, ResearchRoadmapAgent)), None)
        if roadmap_agent and papers:
            roadmap_result = roadmap_agent.run(papers[0], AgentContext(papers, agent_results, self.graph_memory, objective))
            roadmap = roadmap_result.findings.get("steps", [])
        return WorkflowResult(papers, agent_results, comparisons, trends, roadmap, self.graph_memory.stats())

    def compile_langgraph(self) -> Any:
        """Compile a LangGraph state graph when LangGraph is installed."""

        if importlib.util.find_spec("langgraph") is None:
            raise RuntimeError("Install the langgraph extra to compile a LangGraph workflow: pip install .[langgraph]")
        from langgraph.graph import END, StateGraph

        def run_agents(state: dict[str, Any]) -> dict[str, Any]:
            papers = state["papers"]
            result = self.run_research_workflow(papers, objective=state.get("objective"))
            state["workflow_result"] = result
            return state

        graph = StateGraph(dict)
        graph.add_node("run_agents", run_agents)
        graph.set_entry_point("run_agents")
        graph.add_edge("run_agents", END)
        return graph.compile()


def build_default_orchestrator(*, graph_memory: InMemoryResearchGraph | None = None) -> AgentOrchestrator:
    """Build the default eight-agent V4 orchestration stack."""

    return AgentOrchestrator(
        [
            SummarizerAgent(),
            MethodologyAgent(),
            CitationAgent(),
            WeaknessDetectorAgent(),
            TrendAnalysisAgent(),
            ResearchRoadmapAgent(),
            PaperComparisonAgent(),
            FlashcardAgent(),
        ],
        graph_memory=graph_memory,
    )
