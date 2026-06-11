# Arxiv Research Copilot

Arxiv Research Copilot is a production-minded V1 research workflow system for turning an arXiv paper ID into structured AI research notes. It fetches arXiv metadata, downloads the paper PDF, extracts full text, summarizes the paper with an OpenAI-compatible LLM, optionally syncs the notes into Notion, and stores a structured JSON summary locally.

The V1 scope is intentionally single-machine and single-user, while the package layout is designed to evolve toward autonomous paper monitoring, semantic search, vector databases, research graphs, AI agents, and collaborative research workspaces.

## Features

- Fetch paper metadata from the official arXiv API by arXiv ID.
- Download source PDFs into `data/raw_pdfs/`.
- Extract text from all PDF pages using PyMuPDF.
- Generate structured research notes with an OpenAI-compatible API.
- Create Notion pages with the generated notes when Notion credentials are configured.
- Persist every structured result as JSON under `data/summaries/`.
- Expose both a Python pipeline function and a FastAPI HTTP API.

## Repository Structure

```text
arxiv-research-copilot/
├── README.md
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── src/
│   └── arxiv_copilot/
│       ├── config.py
│       ├── models.py
│       ├── main.py
│       ├── arxiv/client.py
│       ├── fetch/pdf_downloader.py
│       ├── extract/extractor.py
│       ├── summarize/prompts.py
│       ├── summarize/summarizer.py
│       ├── notion/client.py
│       └── storage/local_store.py
├── data/
│   ├── raw_pdfs/
│   ├── extracted/
│   └── summaries/
└── tests/
    └── test_basic.py
```

## Setup

### 1. Create a virtual environment

```bash
cd arxiv-research-copilot
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```bash
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
NOTION_TOKEN=secret_your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
APP_DATA_DIR=data
REQUEST_TIMEOUT_SECONDS=30
MAX_PAPER_TEXT_CHARS=120000
```

Notion sync is skipped when `NOTION_TOKEN` or `NOTION_DATABASE_ID` is missing. The pipeline still downloads, extracts, summarizes, and saves the local JSON result.

## Running the Pipeline

Run the pipeline from the command line:

```bash
PYTHONPATH=src python -m arxiv_copilot.main 1706.03762
```

Run the FastAPI server:

```bash
PYTHONPATH=src uvicorn arxiv_copilot.main:app --reload
```

Process a paper over HTTP:

```bash
curl -X POST http://localhost:8000/papers/process \
  -H "Content-Type: application/json" \
  -d '{"arxiv_id":"1706.03762"}'
```

## Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

The service mounts `./data` into the container so PDFs, extracted text, and summaries persist on the host.

## Architecture Overview

- `config.py` loads environment variables and centralizes runtime paths.
- `models.py` defines the Pydantic domain models: `PaperMetadata`, `PaperSummary`, and `ProcessingResult`.
- `arxiv/client.py` talks to the arXiv API and parses Atom XML.
- `fetch/pdf_downloader.py` downloads and validates PDFs.
- `extract/extractor.py` extracts text from every PDF page with PyMuPDF.
- `summarize/prompts.py` contains the research-focused system prompt and user prompt builder.
- `summarize/summarizer.py` calls an OpenAI-compatible chat completion endpoint and validates JSON output.
- `notion/client.py` creates a Notion page with structured sections.
- `storage/local_store.py` persists structured JSON summaries.
- `main.py` wires the modules into `run_pipeline(arxiv_id: str)` and exposes FastAPI routes.

## Notion Database Requirements

The default Notion client expects a database with these properties:

- `Name`: title
- `arXiv ID`: rich text
- `Published`: date
- `PDF`: URL

Share the database with your Notion integration before running the pipeline.

## Testing

```bash
PYTHONPATH=src pytest
```

The included tests cover model composition and prompt construction. End-to-end runs require network access plus valid OpenAI credentials.

## Future Roadmap

- Autonomous arXiv category monitoring and scheduled paper ingestion.
- Multi-paper literature reviews and comparison reports.
- Embedding generation and vector database indexing.
- Semantic search over extracted paper text and generated notes.
- Research graph construction across citations, methods, datasets, and claims.
- Agentic workflows for hypothesis generation, experiment planning, and paper ranking.
- Collaborative Notion workspace templates and richer database schemas.
