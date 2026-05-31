# Arxiv Research Copilot

A multi-version research platform for ingesting, summarizing, indexing, and reasoning over arXiv papers. The repository spans a full progression from a V1 single-paper pipeline to a V18 autonomous scientific research system with persistent memory, multi-agent orchestration, and enterprise Kubernetes deployment.

---

## Repository layout

```
.
├── app/                            # V3 backend (FastAPI + async SQLAlchemy)
├── apps/
│   ├── backend/                    # V5 backend (FastAPI, JWT auth, WebSocket)
│   └── frontend/                   # Next.js 14 research workspace UI
├── arxiv-research-copilot/         # V1 pipeline (arXiv fetch + PDF + OpenAI + Notion)
├── arxiv_paper_summariser_v15/     # V15 simulation and experiment planning engine
├── compliance/                     # Audit event schema and compliance controls
├── deploy/
│   ├── helm/arxiv-summariser/      # Helm chart for V17 enterprise deployment
│   ├── kubernetes/                 # Raw Kubernetes manifests and Kustomize overlays
│   └── monitoring/                 # Prometheus, Alertmanager, Grafana, Loki configs
├── docs/
│   ├── v4_architecture.md          # V4 agent ecosystem design
│   ├── v6-ai-native-research-os.md # V6 AI-native research OS design
│   ├── v12_knowledge_graph.md      # V12 knowledge graph design
│   ├── v14/                        # V14 publication workflow docs
│   ├── v18/                        # V18 autonomous scientific workflow docs
│   └── enterprise/                 # V17 architecture and operations docs
├── infra/terraform/                # AWS infrastructure (EKS, RDS, ElastiCache, S3)
├── migrations/                     # Alembic migrations for V3 schema
├── monitoring/                     # Grafana dashboards and Prometheus rules
├── policies/                       # OPA/Gatekeeper Kubernetes admission policies
├── research_discovery/             # V11 personalized feed and ranking system
├── scripts/                        # deploy.sh, tenantctl.sh, collect-evidence.sh
├── src/
│   ├── arxiv_copilot/              # V2 pipeline (chunking, LLM, citations, storage)
│   ├── arxiv_kg_v12/               # V12 knowledge graph (schema, extraction, traversal, viz)
│   ├── arxiv_paper_summariser/     # V8-V16 literature review, tutoring, multimodal platform
│   ├── arxiv_research_copilot_v4/  # V4 eight-agent orchestration and monitoring
│   └── research_cloud/             # V7 collaborative CRDT sync engine
└── tests/                          # pytest suites for V2-V16 modules
```

---

## Version history

The codebase contains each generation of the platform, kept intact so you can follow the progression or run any version independently.

**V1** (`arxiv-research-copilot/`) is the original single-machine pipeline. You give it an arXiv ID, it downloads the PDF, extracts text with PyMuPDF, sends it to an OpenAI-compatible model, optionally syncs to Notion, and saves a structured JSON summary locally.

**V2** (`src/arxiv_copilot/`) adds intelligent chunking, retry logic, Semantic Scholar enrichment, flashcard generation, citation extraction, and a CLI that can process batches or entire arXiv categories. The heuristic LLM client means it works offline without API credentials.

**V3** (`app/`) is the first production-quality API version. It uses async FastAPI, PostgreSQL via SQLAlchemy, Redis, and either an in-memory or Qdrant vector store. Papers are stored with their embeddings, processed through a background job queue, and served via semantic search, related-paper lookup, and trending endpoints.

**V4** (`src/arxiv_research_copilot_v4/`) introduces eight specialized agents: Summarizer, Methodology, Citation, Weakness Detector, Trend Analysis, Research Roadmap, Paper Comparison, and Flashcard. An `AgentOrchestrator` coordinates them with an in-memory Neo4j-compatible graph, daily arXiv monitoring, and an optional LangGraph compilation path.

**V5** (`apps/backend/`, `apps/frontend/`) is the full-stack SaaS version. The backend adds JWT authentication with RBAC roles, collaborative workspaces, WebSocket presence, and a paper relationship graph. The Next.js frontend includes a dashboard, research feed, graph canvas, paper chat, and team workspace page.

**V6** (`docs/v6-ai-native-research-os.md`) describes the architecture for a persistent AI research OS with multimodal paper understanding (figures, equations, tables), self-improving memory, a PI agent, and multiple autonomy levels. The design feeds directly into V16's implementation.

**V7** (`src/research_cloud/`) implements the collaborative cloud layer. It includes a CRDT-style sync engine for notes and literature reviews, role-based permissions, shared workspace state, and real-time operation merging. Full test coverage in `tests/test_v7_collaboration.py`.

**V8** (`src/arxiv_paper_summariser/engine.py` and related files) is the literature review engine. Given a set of paper records, it clusters them by topic using TF-IDF and Jaccard similarity, traces citation links, detects contradictions, performs gap analysis, and outputs a fully formatted Markdown literature review with bibliography.

**V9** (`src/arxiv_paper_summariser/v9/`) generates implementation artifacts from paper text: pseudo-code blocks, architecture graphs, dependency reports, experiment configurations, reproducibility findings, and a complete starter repository scaffold including PyTorch model skeletons and training scripts.

**V10** (`docs/v10/`) defines the autonomous AI scientist architecture with theory agents, experiment agents, reviewer agents, novelty agents, and research gap agents coordinating through shared scientific memory stores.

**V11** (`research_discovery/`) is the personalized feed system. It tracks user interactions (views, dwells, likes, saves, completions), builds affinity profiles per topic and author, and generates TikTok-style mixed feeds with trending, subscription, and continue-learning lanes.

**V12** (`src/arxiv_kg_v12/`) is the knowledge graph platform. It defines a typed property graph schema (Paper, Author, Dataset, Model, Method, Conference, Benchmark) with six edge types, validates constraints on insertion, and provides traversal APIs, relationship extraction from paper text, and Cytoscape.js/Mermaid visualization export.

**V13** (`src/arxiv_paper_summariser/platform.py`, `curriculum.py`, `tutoring.py`) adds adaptive educational experiences. The curriculum generator builds concept dependency graphs from paper text, then produces explanations calibrated to four learner modes (Beginner through Researcher), quizzes, learning roadmaps, and mini-courses. The tutoring engine adapts scaffolding in real time.

**V14** (`docs/v14/`) documents the publication workflow toolset: reviewer simulation with multiple personas, citation intelligence tools (suggestion, claim checking, novelty analysis, plagiarism detection), formatting pipelines for venue compliance, and rebuttal workspaces.

**V15** (`arxiv_paper_summariser_v15/`) is a pre-implementation simulation engine. You define architecture specs and experiment configurations, and the engine estimates GPU hours, costs, benchmark predictions (ROUGE-L, faithfulness, citation F1, latency), and ablation impacts without running any actual training.

**V16** (`src/arxiv_paper_summariser/platform_v16.py`) is the multimodal understanding platform. It routes paper assets through modality-specific parsers: figure understanding, chart reasoning (trend extraction from series data), equation interpretation (variable extraction, operator analysis), architecture diagram parsing (component and edge graphs), table extraction, and video understanding from transcripts and frame annotations.

**V17** (`deploy/`, `infra/`, `monitoring/`, `compliance/`) is the enterprise deployment stack. It covers multi-tenant Kubernetes with namespace isolation and ResourceQuotas, OIDC/SSO integration, KEDA queue autoscaling, OPA admission policies, immutable audit log storage on S3, Terraform modules for AWS EKS/RDS/ElastiCache, Grafana dashboards, and Prometheus alerting rules.

**V18** (`docs/v18/`) defines the persistent cognitive platform with five memory layers (working, episodic, semantic, procedural, strategic), eight autonomous workflows (literature discovery, summarization, cross-domain synthesis, hypothesis generation, experiment design, critique, self-improvement, long-term program management), and a full orchestration system with governance gates.

---

## Quickstart

### V1 pipeline (fastest to run)

```bash
cd arxiv-research-copilot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY
PYTHONPATH=src python -m arxiv_copilot.main 1706.03762
```

The pipeline fetches the Attention Is All You Need paper, downloads the PDF, extracts text, generates structured notes, and saves them to `data/summaries/`.

To run the FastAPI server instead:

```bash
PYTHONPATH=src uvicorn arxiv_copilot.main:app --reload
curl -X POST http://localhost:8000/papers/process \
  -H "Content-Type: application/json" \
  -d '{"arxiv_id":"1706.03762"}'
```

### V3 backend

```bash
# Start infrastructure
docker compose up -d

# Install dependencies and run migrations
pip install -r requirements.txt
alembic upgrade head

# Start the API
uvicorn app.main:app --reload
```

The API is at `http://localhost:8000/api/v3`. Key endpoints:

```
GET  /api/v3/papers              list papers with optional topic filter
POST /api/v3/papers              upsert a paper
GET  /api/v3/search?q=<query>    semantic + keyword hybrid search
GET  /api/v3/related/<paper_id>  related papers by embedding similarity
GET  /api/v3/trending            papers ranked by views and search activity
POST /api/v3/process             enqueue background embedding/indexing jobs
POST /api/v3/memory/events       record a user reading event
GET  /api/v3/memory/users/<id>   get user interest profile
```

### V5 full-stack app

```bash
# Backend
cd apps/backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal)
npm install
npm --workspace apps/frontend run dev
```

Open `http://localhost:3000`. Log in with `founder@arxivcopilot.ai` / `research`. The dashboard, feed, graph, paper chat, and workspace pages are all wired to the backend.

### V2 CLI

```bash
# Process a single paper
python -m arxiv_copilot --arxiv-id 1706.03762

# Process 5 newest papers from cs.AI
python -m arxiv_copilot --category cs.AI --max-results 5 --no-pdf

# Batch processing
python -m arxiv_copilot --arxiv-id 1706.03762 --arxiv-id 2005.14165
```

---

## Running tests

```bash
# Install test dependencies (from root or apps/backend)
pip install pytest httpx sentence-transformers pydantic-settings apscheduler

# Run all tests
pytest tests/ apps/backend/tests/

# Run a specific module
pytest tests/test_v7_collaboration.py -v
pytest tests/test_v12_knowledge_graph.py -v
pytest tests/test_research_discovery.py -v
```

The test suite covers V2-V16 across chunking, retry logic, the full pipeline, personalized feeds, the knowledge graph, V7 CRDT sync, V8 literature reviews, V9 implementation workflows, V13 adaptive tutoring, V15 simulation, V16 multimodal parsing, and the V5 API.

---

## Configuration

### V1 / V2

Environment variables (copy `.env.example` to `.env`):

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | required | OpenAI or compatible API key |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | LLM endpoint |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model name |
| `NOTION_TOKEN` | optional | Notion integration token |
| `NOTION_DATABASE_ID` | optional | Target Notion database |
| `APP_DATA_DIR` | `data` | Local storage root |
| `MAX_PAPER_TEXT_CHARS` | `120000` | PDF text truncation limit |

### V3

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/arxiv_copilot` | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `VECTOR_BACKEND` | `memory` | `memory` or `qdrant` |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant endpoint (if used) |
| `EMBEDDING_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `EMBEDDING_DIMENSION` | `384` | Vector dimension |
| `WORKER_INTERVAL_SECONDS` | `60` | Background job polling interval |

### V5 backend

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET` | `change-me-in-production` | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_MINUTES` | `720` | Token expiry |

---

## Architecture overview

### V3 service layer

The V3 backend follows a clean repository/service pattern. Routes delegate to service classes, which call repository classes, which interact with SQLAlchemy models. The dependency injection happens in `app/core/dependencies.py`. Vector operations go through the `VectorStore` protocol, backed by either `InMemoryVectorStore` or `QdrantVectorStore` depending on the `VECTOR_BACKEND` setting.

Background jobs are queued via `ProcessingJob` records in PostgreSQL. The `BackgroundScheduler` from APScheduler polls every `WORKER_INTERVAL_SECONDS` and claims one job at a time using `SELECT ... FOR UPDATE SKIP LOCKED` to prevent duplicate processing.

Embeddings fall back to a deterministic SHA-256 hash embedding if the sentence-transformers model fails to load, so the API always returns results even without the ML dependency.

### V7 sync engine

The CRDT sync engine in `src/research_cloud/sync_engine.py` uses an RGA (Replicated Growable Array) approach for text. Each character is an immutable atom with a stable `OperationId(counter, actor)`. Concurrent inserts from different actors are ordered by `OperationId` comparison, so all peers converge to the same text regardless of operation arrival order. Deletes are tombstones, not physical removals, which makes replays safe. Metadata fields use last-writer-wins by `OperationId`.

### V12 knowledge graph

`KnowledgeGraph` is an in-memory directed property graph with schema validation. Every `add_node` call checks required properties against `NODE_SPECS` and every `add_edge` call checks source/target type compatibility against `EDGE_SPECS`. The `RelationshipExtractionPipeline` uses regex patterns to detect datasets (ImageNet, SQuAD, etc.), models (BERT, GPT-4, etc.), methods (LoRA, chain-of-thought, etc.), and semantic relationships (improvement language, contradiction language, inspiration language) from paper titles and abstracts.

---

## Deployment

### Docker Compose (local)

```bash
# V3 infrastructure only
docker compose up -d postgres redis qdrant

# V1 all-in-one
cd arxiv-research-copilot && docker compose up --build
```

### Kubernetes (V5)

```bash
kubectl apply -f deploy/kubernetes/namespace.yaml
kubectl apply -f deploy/kubernetes/backend.yaml
kubectl apply -f deploy/kubernetes/frontend.yaml
kubectl apply -f deploy/kubernetes/ingress.yaml
```

### Helm (V17 enterprise)

```bash
# Plan (dry run)
./scripts/deploy.sh plan

# Deploy to staging or production
NAMESPACE=arxiv-prod ./scripts/deploy.sh deploy

# Rollback
NAMESPACE=arxiv-prod ./scripts/deploy.sh rollback
```

The Helm chart at `deploy/helm/arxiv-summariser/` provisions API and worker Deployments, Services, HPA for the API, a KEDA ScaledObject for the worker queue, ConfigMaps, RBAC, NetworkPolicies, and per-tenant ResourceQuotas. Values are in `values.yaml`.

### Terraform (AWS)

```bash
cd infra/terraform
terraform init
terraform plan -var environment=staging
terraform apply
```

The Terraform modules create a private EKS cluster, an encrypted multi-AZ RDS PostgreSQL instance with 35-day backups, an ElastiCache Redis replication group, an S3 bucket for papers, and a separate S3 bucket with Object Lock for immutable audit logs.

### Tenant provisioning

```bash
TENANT=myorg CPU_QUOTA=8 MEMORY_QUOTA=32Gi ./scripts/tenantctl.sh myorg
```

---

## CI/CD

Three GitHub Actions workflows:

`ci.yml` runs on every push and pull request. It installs Python 3.12 and runs pytest for the backend, installs Node 20 and builds the frontend, then builds both Docker images.

`enterprise-ci-cd.yml` runs on pushes to `main`. It validates Terraform formatting and schema, lints the Helm chart, runs a Trivy filesystem security scan for CRITICAL/HIGH vulnerabilities, and then deploys to staging automatically followed by production with manual approval.

---

## Compliance and security

The V17 stack includes OPA/Gatekeeper admission policies in `policies/gatekeeper-requirements.yaml` that enforce CPU resource requests, non-root container execution, and no mutable `latest` image tags on all pods.

Audit events follow the JSON schema in `compliance/audit-event-schema.json`. Required fields include `event_id`, `event_time`, `tenant_id`, `actor` (with subject and type), `action`, `resource`, `result`, and `correlation_id`. Events are classified as public, internal, confidential, or restricted per the data classes in `compliance/controls.md`.

Evidence collection for compliance reviews runs via:

```bash
./scripts/collect-evidence.sh evidence/$(date -u +%Y%m%dT%H%M%SZ)
```

This exports namespace labels, deployment states, NetworkPolicies, ResourceQuotas, and RBAC bindings to a timestamped directory.

---

## Python packages by version

V1: `fastapi`, `uvicorn`, `requests`, `pymupdf`, `openai`, `notion-client`, `pydantic`, `rich`

V2 adds: `pypdf` (optional PDF backend), standard library only for core path

V3 adds: `sqlalchemy[asyncpg]`, `alembic`, `sentence-transformers`, `qdrant-client`, `apscheduler`, `pydantic-settings`, `redis`

V4 adds: `langgraph` (optional), `neo4j` (optional)

V5 adds: `PyJWT`, `email-validator`, `httpx`

Frontend: `next@14`, `react@18`, `@tanstack/react-query`, `framer-motion`, `zustand`, `lucide-react`, `tailwindcss`, `typescript`

---

## License

MIT
