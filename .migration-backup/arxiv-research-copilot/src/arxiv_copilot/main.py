"""FastAPI app and executable pipeline for Arxiv Research Copilot."""

from __future__ import annotations

import argparse

from fastapi import FastAPI
from pydantic import BaseModel
from rich.console import Console

from arxiv_copilot.arxiv import ArxivClient
from arxiv_copilot.config import get_settings
from arxiv_copilot.extract import PdfTextExtractor
from arxiv_copilot.fetch import PdfDownloader
from arxiv_copilot.models import ProcessingResult
from arxiv_copilot.notion import NotionResearchClient
from arxiv_copilot.storage import LocalStore
from arxiv_copilot.summarize import PaperSummarizer

console = Console()
app = FastAPI(title="Arxiv Research Copilot", version="0.1.0")


class PipelineRequest(BaseModel):
    """API request body for processing a single arXiv paper."""

    arxiv_id: str


class PipelineResponse(BaseModel):
    """API response body containing the processing result and local file path."""

    result: ProcessingResult
    local_summary_path: str
    notion_page_id: str | None


def run_pipeline(arxiv_id: str) -> ProcessingResult:
    """Run the full arXiv-to-Notion research workflow for one paper."""
    settings = get_settings()
    arxiv_client = ArxivClient(settings)
    downloader = PdfDownloader(settings)
    extractor = PdfTextExtractor(settings)
    summarizer = PaperSummarizer(settings)
    store = LocalStore(settings)

    console.log(f"Fetching metadata for {arxiv_id}")
    metadata = arxiv_client.fetch_by_id(arxiv_id)

    console.log(f"Downloading PDF from {metadata.pdf_url}")
    pdf_path = downloader.download(metadata)

    console.log(f"Extracting text from {pdf_path}")
    paper_text = extractor.extract(pdf_path, metadata.arxiv_id)

    console.log("Generating structured research summary")
    summary = summarizer.summarize(metadata, paper_text)
    result = ProcessingResult(metadata=metadata, summary=summary)

    if settings.notion_enabled:
        console.log("Syncing summary to Notion")
        notion_page_id = NotionResearchClient(settings).create_paper_page(result)
        console.log(f"Created Notion page: {notion_page_id}")
    else:
        console.log("Skipping Notion sync because NOTION_TOKEN or NOTION_DATABASE_ID is not configured")

    summary_path = store.save_summary(result)
    console.log(f"Saved local summary: {summary_path}")
    return result


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/papers/process", response_model=PipelineResponse)
def process_paper(request: PipelineRequest) -> PipelineResponse:
    """Process a single paper from an HTTP request."""
    result = run_pipeline(request.arxiv_id)
    settings = get_settings()
    local_path = settings.summaries_dir / f"{request.arxiv_id.replace('/', '_').replace(':', '_')}.json"
    return PipelineResponse(result=result, local_summary_path=str(local_path), notion_page_id=None)


def main() -> None:
    """Command-line entry point for running the pipeline."""
    parser = argparse.ArgumentParser(description="Run the Arxiv Research Copilot pipeline for one paper.")
    parser.add_argument("arxiv_id", help="arXiv ID, for example 1706.03762")
    args = parser.parse_args()
    result = run_pipeline(args.arxiv_id)
    console.print_json(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
