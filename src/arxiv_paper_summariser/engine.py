"""Literature synthesis engine for V8 review generation."""

from __future__ import annotations

from .analysis import (
    analyze_chronology,
    analyze_gaps,
    build_citation_graph,
    detect_contradictions,
    trend_evolution_summary,
)
from .citations import CitationFormatter
from .clustering import ClusteringPipeline
from .models import ComparisonTable, Paper, Review, ReviewConfig, ReviewSection, TopicCluster
from .text import first_sentence


class LiteratureSynthesisEngine:
    """Generate complete, citation-aware literature reviews from papers."""

    def __init__(
        self,
        config: ReviewConfig | None = None,
        clustering_pipeline: ClusteringPipeline | None = None,
    ) -> None:
        self.config = config or ReviewConfig()
        self.clustering_pipeline = clustering_pipeline or ClusteringPipeline()
        self.formatter = CitationFormatter(self.config.citation_style)

    def generate_review(self, papers: list[Paper]) -> Review:
        """Generate a complete V8 literature review artifact."""

        ordered = sorted(papers, key=lambda paper: (paper.year, paper.title))
        clusters = self.clustering_pipeline.run(
            ordered,
            max_keywords=self.config.max_cluster_keywords,
            min_cluster_size=self.config.min_cluster_size,
        )
        citation_graph = build_citation_graph(ordered)
        chronology = analyze_chronology(ordered, clusters) if self.config.include_trends else ()
        contradictions = detect_contradictions(ordered) if self.config.include_contradictions else ()
        gaps = analyze_gaps(ordered, clusters) if self.config.include_gap_analysis else ()
        sections = self._build_sections(ordered, clusters, chronology, contradictions, gaps)
        tables = (self._comparison_table(ordered),) if self.config.include_method_table else ()
        return Review(
            title=self.config.title,
            sections=sections,
            bibliography=self.formatter.bibliography(ordered),
            clusters=clusters,
            citation_graph=citation_graph,
            chronology=chronology,
            contradictions=contradictions,
            gaps=gaps,
            comparison_tables=tables,
        )

    def _build_sections(
        self,
        papers: list[Paper],
        clusters: tuple[TopicCluster, ...],
        chronology,
        contradictions,
        gaps: tuple[str, ...],
    ) -> tuple[ReviewSection, ...]:
        sections: list[ReviewSection] = [self._overview_section(papers, clusters)]
        sections.extend(self._theme_section(cluster, papers) for cluster in clusters)
        if self.config.include_trends:
            sections.append(self._chronology_section(chronology))
        if self.config.include_contradictions:
            sections.append(self._contradiction_section(contradictions))
        if self.config.include_gap_analysis:
            sections.append(self._gap_section(gaps))
        sections.append(self._conclusion_section(papers, clusters))
        return tuple(sections)

    def _overview_section(self, papers: list[Paper], clusters: tuple[TopicCluster, ...]) -> ReviewSection:
        citations = self._citations_for(papers)
        years = [paper.year for paper in papers]
        body = (
            f"This review synthesizes {len(papers)} paper(s) published "
            f"between {min(years) if years else 'n/a'} and {max(years) if years else 'n/a'}. "
            f"The clustering pipeline identifies {len(clusters)} thematic group(s): "
            f"{'; '.join(cluster.label for cluster in clusters) or 'none'}. "
            f"The synthesis is citation-aware and traces both direct citation links and topical similarity {', '.join(citations)}."
        )
        return ReviewSection("Overview", body, tuple(citations), tuple(paper.id for paper in papers))

    def _theme_section(self, cluster: TopicCluster, papers: list[Paper]) -> ReviewSection:
        paper_by_id = {paper.id: paper for paper in papers}
        cluster_papers = [paper_by_id[paper_id] for paper_id in cluster.paper_ids]
        citations = self._citations_for(cluster_papers)
        evidence = []
        for paper in cluster_papers:
            evidence.append(
                f"{first_sentence(paper.summary or paper.abstract, paper.title)} {self.formatter.in_text(paper)}"
            )
        body = (
            f"Theme keywords: {', '.join(cluster.keywords)}. "
            f"{cluster.summary} "
            f"Evidence: {' '.join(evidence)}"
        )
        return ReviewSection(f"Theme: {cluster.label}", body, tuple(citations), cluster.paper_ids)

    def _chronology_section(self, chronology) -> ReviewSection:
        body = trend_evolution_summary(chronology)
        if chronology:
            body += " " + " ".join(point.description for point in chronology)
        return ReviewSection(
            "Chronology and Trend Evolution",
            body,
            (),
            tuple(paper_id for point in chronology for paper_id in point.paper_ids),
        )

    @staticmethod
    def _contradiction_section(contradictions) -> ReviewSection:
        if not contradictions:
            body = "No strong contradictions were detected from the supplied claims and findings."
            paper_ids: tuple[str, ...] = ()
        else:
            body = " ".join(
                f"{item.description} Confidence: {item.confidence:.2f}." for item in contradictions
            )
            paper_ids = tuple(paper_id for item in contradictions for paper_id in item.paper_ids)
        return ReviewSection("Contradiction Analysis", body, (), paper_ids)

    @staticmethod
    def _gap_section(gaps: tuple[str, ...]) -> ReviewSection:
        body = " ".join(f"Gap {index}: {gap}" for index, gap in enumerate(gaps, start=1))
        return ReviewSection("Gap Analysis", body, (), ())

    def _conclusion_section(self, papers: list[Paper], clusters: tuple[TopicCluster, ...]) -> ReviewSection:
        citations = self._citations_for(papers[-3:])
        body = (
            "Collectively, the reviewed work supports a structured literature narrative around "
            f"{', '.join(cluster.label for cluster in clusters[:3]) or 'the supplied corpus'}. "
            "The strongest review sections should combine thematic evidence, chronology, contradictions, and gaps "
            f"rather than treating summaries as isolated abstracts {', '.join(citations)}."
        )
        return ReviewSection("Synthesis and Implications", body, tuple(citations), tuple(paper.id for paper in papers))

    def _comparison_table(self, papers: list[Paper]) -> ComparisonTable:
        rows = []
        for paper in papers:
            methods = ", ".join(paper.methods) or "Not specified"
            findings = ", ".join(paper.findings) or first_sentence(paper.summary or paper.abstract, paper.title)
            limitations = ", ".join(paper.limitations) or "Not specified"
            rows.append((paper.title, str(paper.year), methods, findings, limitations))
        return ComparisonTable(
            headers=("Paper", "Year", "Method", "Finding", "Limitation"),
            rows=tuple(rows),
        )

    def _citations_for(self, papers: list[Paper]) -> list[str]:
        bibliography_order = {paper.id: index for index, paper in enumerate(sorted(papers, key=lambda item: (item.lead_author, item.year, item.title)), start=1)}
        return [self.formatter.in_text(paper, bibliography_order[paper.id]) for paper in papers]
