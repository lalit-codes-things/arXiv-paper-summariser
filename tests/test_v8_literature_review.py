from arxiv_paper_summariser import LiteratureSynthesisEngine, Paper, ReviewConfig
from arxiv_paper_summariser.citations import CitationFormatter
from arxiv_paper_summariser.clustering import ClusteringPipeline
from arxiv_paper_summariser.models import CitationStyle
from arxiv_paper_summariser.workflows import ReviewGenerationWorkflow


def sample_papers():
    return [
        Paper(
            id="p1",
            title="Neural Retrieval for Scientific Discovery",
            authors=("Ada Smith", "Grace Kim"),
            year=2020,
            abstract="Neural retrieval improves discovery across scientific corpora.",
            summary="Neural retrieval improves citation recommendation for scientific discovery.",
            keywords=("retrieval", "citations", "scientific discovery"),
            citations=(),
            claims=("retrieval improves discovery",),
            methods=("dual encoder",),
            findings=("improved citation recommendation",),
            limitations=("limited evaluation outside computer science",),
        ),
        Paper(
            id="p2",
            title="Graph Citations for Literature Synthesis",
            authors=("Lin Rao",),
            year=2022,
            abstract="Citation graphs improve synthesis of related work.",
            summary="Citation graphs improve evidence linking in literature synthesis.",
            keywords=("citations", "synthesis", "graphs"),
            citations=("p1",),
            claims=("citation graphs improve synthesis",),
            methods=("graph ranking",),
            findings=("robust evidence linking",),
        ),
        Paper(
            id="p3",
            title="Limits of Neural Retrieval in Noisy Archives",
            authors=("Mina Patel",),
            year=2024,
            abstract="Neural retrieval fails on noisy archives and remains limited by sparse metadata.",
            summary="Neural retrieval fails when metadata are noisy and sparse.",
            keywords=("retrieval", "metadata", "archives"),
            citations=("p1",),
            claims=("retrieval fails on noisy archives",),
            methods=("stress test",),
            findings=("unstable retrieval quality",),
            limitations=("open challenge for multilingual archives",),
        ),
    ]


def test_engine_generates_complete_literature_review():
    review = LiteratureSynthesisEngine(ReviewConfig(title="V8 Review")).generate_review(sample_papers())

    section_titles = [section.title for section in review.sections]
    assert review.title == "V8 Review"
    assert "Overview" in section_titles
    assert "Chronology and Trend Evolution" in section_titles
    assert "Contradiction Analysis" in section_titles
    assert "Gap Analysis" in section_titles
    assert review.bibliography
    assert review.comparison_tables[0].headers == ("Paper", "Year", "Method", "Finding", "Limitation")
    assert any(link.source_id == "p2" and link.target_id == "p1" for link in review.citation_graph)
    assert review.contradictions
    assert review.gaps


def test_clustering_pipeline_groups_related_topics():
    clusters = ClusteringPipeline(similarity_threshold=0.05).run(sample_papers(), max_keywords=5)

    assert clusters
    assert any("Retrieval" in cluster.label or "Citation" in cluster.label for cluster in clusters)
    assert sorted(paper_id for cluster in clusters for paper_id in cluster.paper_ids) == ["p1", "p2", "p3"]


def test_citation_formatter_supports_ieee_bibliography():
    paper = sample_papers()[0]
    formatter = CitationFormatter(CitationStyle.IEEE)

    assert formatter.in_text(paper, 1) == "[1]"
    assert formatter.bibliography_entry(paper, 1).startswith("[1] Ada Smith & Grace Kim")


def test_workflow_exports_markdown(tmp_path):
    records = [paper.__dict__ for paper in sample_papers()]
    review = ReviewGenerationWorkflow().from_records(records)
    output = ReviewGenerationWorkflow().export_markdown(review, tmp_path / "review.md")

    text = output.read_text(encoding="utf-8")
    assert "# Structured Literature Review" in text
    assert "## Bibliography" in text
    assert "| Paper | Year | Method | Finding | Limitation |" in text
