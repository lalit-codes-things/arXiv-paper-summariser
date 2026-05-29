# Arxiv Research Copilot V3

V3 turns the original arXiv paper summariser into a backend-first AI research platform. The new system provides a FastAPI REST API, PostgreSQL persistence, async repository/service layers, an embeddings pipeline, vector search, background processing, and a research memory model.

## Architecture

```text
FastAPI API
  ├── /papers, /paper/{id}, /process
  ├── /search, /related/{id}, /trending
  └── /memory/events, /memory/users/{id}
        │
Services layer
  ├── PaperService          CRUD + processing queue orchestration
  ├── SearchService         semantic + keyword retrieval
  ├── IndexingService       chunk extraction + embeddings + vector upsert
  ├── MemoryService         viewed papers, interests, topic clusters
  └── TrendingService       activity-based discovery
        │
Repositories
  ├── PaperRepository
  ├── ProcessingJobRepository
  └── MemoryRepository
        │
Storage
  ├── PostgreSQL via async SQLAlchemy
  ├── Qdrant vector database (or local in-memory vector store)
  └── Redis-ready worker configuration
```

## Key capabilities

- **Semantic search** over embedded paper titles, abstracts, summaries, methodologies, topics, and contributions.
- **Vector pipeline** that chunks paper fields, generates embeddings with `sentence-transformers`, and writes vectors to Qdrant or an in-memory backend.
- **Research memory** tracking per-user viewed papers, interests, topic clusters, and reading history.
- **Background workers** powered by APScheduler with a standalone worker entry point for queued summarization, embedding, and indexing jobs.
- **Search indexing** for title, abstract, topics, contributions, and methodology in relational and vector stores.
- **Scalable backend architecture** with dependency injection, repository pattern, async SQLAlchemy sessions, and swappable vector store interfaces.

## API endpoints

All application endpoints are prefixed with `/api/v3`.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/papers` | List papers with pagination and optional topic filter. |
| `POST` | `/papers` | Upsert a paper and its searchable metadata. |
| `GET` | `/paper/{paper_id}` | Fetch a paper and record a view metric. |
| `PATCH` | `/paper/{paper_id}` | Update paper metadata, summary, topics, or contributions. |
| `POST` | `/process` | Queue paper summarization, embedding, and indexing work. |
| `GET` | `/search?q=...` | Run semantic search with keyword fallback. |
| `GET` | `/related/{paper_id}` | Find semantically related papers. |
| `GET` | `/trending` | Return recently active papers ranked by views/searches. |
| `POST` | `/memory/events` | Record reading-memory events. |
| `GET` | `/memory/users/{user_id}` | Return user interests and topic clusters. |

## Configuration

Settings are loaded from environment variables or `.env`.

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/arxiv_copilot
REDIS_URL=redis://localhost:6379/0
VECTOR_BACKEND=qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=arxiv_papers
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

Use `VECTOR_BACKEND=memory` for local development without Qdrant.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```

Process one queued job manually:

```bash
python scripts/worker.py
```

## Example indexing flow

1. `POST /api/v3/papers` to create or update a paper.
2. `POST /api/v3/process` with `task_type=full_pipeline` to queue embedding/indexing.
3. Run `python scripts/worker.py` or start the API scheduler.
4. Query `GET /api/v3/search?q=papers about small language models for education`.
