"""End-to-end research copilot pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from arxiv_copilot.arxiv import ArxivClient
from arxiv_copilot.citations import extract_citations
from arxiv_copilot.chunking import ChunkingConfig, PaperChunker
from arxiv_copilot.enrich import SemanticScholarClient
from arxiv_copilot.flashcards import flashcards_from_summary
from arxiv_copilot.llm import HeuristicLLMClient, LLMClient, SummarizationEngine
from arxiv_copilot.notion import NotionSync
from arxiv_copilot.pdf import PDFService
from arxiv_copilot.schemas import ArxivPaper, PaperResult
from arxiv_copilot.storage import JSONStorage

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineConfig:
    download_pdfs: bool = True
    enrich_semantic_scholar: bool = True
    sync_notion: bool = False
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)


@dataclass(slots=True)
class ResearchCopilotPipeline:
    arxiv: ArxivClient = field(default_factory=ArxivClient)
    pdf: PDFService = field(default_factory=PDFService)
    storage: JSONStorage = field(default_factory=JSONStorage)
    semantic_scholar: SemanticScholarClient = field(default_factory=SemanticScholarClient)
    notion: NotionSync = field(default_factory=NotionSync)
    llm: LLMClient = field(default_factory=HeuristicLLMClient)
    config: PipelineConfig = field(default_factory=PipelineConfig)

    def process_arxiv_id(self, arxiv_id: str) -> PaperResult:
        paper = self.arxiv.fetch_by_id(arxiv_id)
        return self.process_paper(paper)

    def process_paper(self, paper: ArxivPaper) -> PaperResult:
        text = paper.abstract
        if self.config.download_pdfs and paper.pdf_url:
            pdf_path = self.pdf.download(paper.pdf_url, paper.arxiv_id)
            text = self.pdf.extract_text(pdf_path)
        engine = SummarizationEngine(llm=self.llm, chunker=PaperChunker(self.config.chunking))
        summary = engine.summarize(title=paper.title, abstract=paper.abstract, text=text)
        summary.flashcards = flashcards_from_summary(summary)
        citations = extract_citations(text)
        semantic = self.semantic_scholar.enrich_arxiv_id(paper.arxiv_id) if self.config.enrich_semantic_scholar else None
        _merge_related_papers(summary, semantic)
        result = PaperResult(paper=paper, summary=summary, citations=citations, semantic_scholar=semantic)
        path = self.storage.save(result)
        LOGGER.info("Saved result for %s to %s", paper.arxiv_id, path)
        if self.config.sync_notion:
            self.notion.sync(result)
        return result

    def process_many(self, arxiv_ids: list[str]) -> list[PaperResult]:
        return [self.process_arxiv_id(arxiv_id) for arxiv_id in arxiv_ids]

    def process_category(self, category: str, *, max_results: int = 10) -> list[PaperResult]:
        return [self.process_paper(paper) for paper in self.arxiv.newest(category, max_results=max_results)]

    def process_newest_ai(self, *, max_results: int = 10) -> list[PaperResult]:
        return self.process_category("cs.AI", max_results=max_results)


def _merge_related_papers(summary, semantic) -> None:
    if not semantic:
        return
    existing = {item.title.lower() for item in summary.suggested_reading if item.title}
    from arxiv_copilot.schemas import SuggestedReading

    for paper in semantic.related_papers[:5]:
        title = paper.get("title")
        if not title or title.lower() in existing:
            continue
        external_ids = paper.get("externalIds") or {}
        summary.suggested_reading.append(
            SuggestedReading(
                title=title,
                reason="Recommended by Semantic Scholar as related work.",
                arxiv_id=external_ids.get("ArXiv"),
                url=paper.get("url"),
                citation_count=paper.get("citationCount"),
            )
        )
        existing.add(title.lower())


def default_pipeline(data_dir: str | Path = "data", *, llm: LLMClient | None = None) -> ResearchCopilotPipeline:
    data_path = Path(data_dir)
    return ResearchCopilotPipeline(
        pdf=PDFService(download_dir=data_path / "pdfs"),
        storage=JSONStorage(root=data_path / "results"),
        llm=llm or HeuristicLLMClient(),
    )
