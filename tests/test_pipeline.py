from pathlib import Path

from arxiv_copilot.pipeline import PipelineConfig, ResearchCopilotPipeline
from arxiv_copilot.schemas import ArxivPaper, SemanticScholarPaper
from arxiv_copilot.storage import JSONStorage


class FakeArxiv:
    def fetch_by_id(self, arxiv_id):
        return ArxivPaper(arxiv_id=arxiv_id, title="A Test Paper", abstract="We propose a method.", authors=["A"])

    def newest(self, category, *, max_results=10):
        return [self.fetch_by_id(f"{category}.{idx}") for idx in range(max_results)]


class FakeSemanticScholar:
    def enrich_arxiv_id(self, arxiv_id):
        return SemanticScholarPaper(
            paper_id="p1",
            citation_count=42,
            influential_citation_count=7,
            related_papers=[{"title": "Related", "url": "https://example.com", "citationCount": 5}],
        )


class FakeNotion:
    def sync(self, result):
        return True


def test_pipeline_batch_processes_and_stores_results(tmp_path: Path):
    pipeline = ResearchCopilotPipeline(
        arxiv=FakeArxiv(),
        storage=JSONStorage(tmp_path),
        semantic_scholar=FakeSemanticScholar(),
        notion=FakeNotion(),
        config=PipelineConfig(download_pdfs=False, enrich_semantic_scholar=True),
    )

    results = pipeline.process_many(["1234.5678", "2345.6789"])

    assert len(results) == 2
    assert results[0].semantic_scholar.citation_count == 42
    assert results[0].summary.flashcards
    assert (tmp_path / "1234.5678.json").exists()
    assert results[0].summary.suggested_reading[0].title == "Related"
