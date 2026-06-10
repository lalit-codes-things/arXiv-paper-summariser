

```markdown
# arXiv Paper Summariser — AI-Native Research Platform

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![Node](https://img.shields.io/badge/node-20%2B-green.svg)](https://nodejs.org)

**A production‑grade, multi‑version research ecosystem that ingests arXiv papers, enables semantic search and AI chat, personalises feeds, builds knowledge graphs, simulates experiments, supports real‑time collaboration, and deploys at enterprise scale.**

---

## 📖 Table of Contents

1. [What is this project?](#-what-is-this-project)
2. [System Architecture](#-system-architecture)
3. [Feature Overview by Version](#-feature-overview-by-version)
4. [Project Directory Structure](#-project-directory-structure)
5. [Quick Start](#-quick-start)
6. [Deployment](#-deployment)
7. [API Reference](#-api-reference)
8. [Configuration](#-configuration)
9. [Development & Testing](#-development--testing)
10. [Contributing](#-contributing)
11. [License](#-license)

---

## 🧠 What is this project?

arXiv Paper Summariser is an **autonomous AI research copilot** that transforms how researchers discover, read, understand, and collaborate on scientific literature. It is not a single tool but a **suite of progressively advanced systems** that together form a research operating system.

| Capability | Description |
|------------|-------------|
| **Paper ingestion** | Fetches metadata, PDFs, and citations from arXiv. |
| **Semantic search** | Hybrid vector + keyword search across thousands of papers. |
| **AI chat** | Ask Claude (or any LLM) any question about a paper. |
| **Personalised feed** | TikTok‑style swipe feed that learns your interests. |
| **Knowledge graph** | Nodes = papers, authors, datasets, methods, benchmarks; Edges = citations, contradictions, improvements. |
| **Multimodal understanding** | OCR, figure/chart/equation/table/diagram parsing. |
| **Research simulation** | Predict benchmark scores, cost, and risk *before* implementing. |
| **Collaboration** | Real‑time workspaces, annotations, shared flashcards, CRDT notes. |
| **Adaptive tutoring** | Turn papers into mini‑courses, quizzes, and Socratic tutoring. |
| **Enterprise deployment** | Kubernetes, SSO, audit logging, multi‑tenancy, SLOs. |

The project is **monorepo‑organized** with multiple backends (V3 research API, V5 auth/collab API), a Next.js frontend, standalone research packages, and full infrastructure as code.

---

## 🏗️ System Architecture

```mermaid
flowchart TB
    subgraph Clients
        Web[Next.js Frontend<br/>Port 3000]
        CLI[CLI / Scripts]
    end

    subgraph APIs
        V3[V3 Research API<br/>Port 8000<br/>FastAPI]
        V5[V5 Auth & Collaboration API<br/>Port 8001<br/>FastAPI]
    end

    subgraph Background
        Worker[Background Workers<br/>APScheduler / KEDA]
        Queue[Redis Queue]
    end

    subgraph Storage
        PG[(PostgreSQL<br/>Papers, profiles, jobs)]
        Qdrant[(Qdrant<br/>Vector index, 384d)]
        S3[(S3 / Object Store<br/>PDFs, figures, exports)]
    end

    subgraph AI
        Claude[Anthropic Claude<br/>Paper chat]
        OpenAI[OpenAI‑compatible<br/>Summarisation]
        ST[Sentence‑Transformers<br/>Embeddings]
    end

    subgraph External
        Arxiv[arXiv API]
        Scholar[Semantic Scholar]
    end

    Web --> V3 & V5
    CLI --> V3
    V3 --> PG & Qdrant & Queue
    V5 --> PG
    Worker --> Queue & PG & Qdrant & Claude & OpenAI
    V3 --> ST & Arxiv & Scholar
    V3 & Worker --> S3
```

### Data Flow for a Typical User Action

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant V3_API
    participant V5_API
    participant DB
    participant Qdrant
    participant Claude

    User->>Frontend: Search query
    Frontend->>V3_API: GET /search?q=...
    V3_API->>V3_API: Embed query
    V3_API->>Qdrant: ANN search
    Qdrant-->>V3_API: Top paper IDs
    V3_API->>DB: Fetch paper details
    DB-->>V3_API: Papers
    V3_API-->>Frontend: Search results
    Frontend-->>User: Display papers

    User->>Frontend: Open paper & ask chat
    Frontend->>V3_API: POST /chat/paper
    V3_API->>DB: Get paper metadata
    V3_API->>Claude: Prompt with abstract + question
    Claude-->>V3_API: Answer
    V3_API->>DB: Record memory event
    V3_API-->>Frontend: Answer + citations
    Frontend-->>User: AI response
```

---

## 📦 Feature Overview by Version

The project evolved through clearly defined milestones. Each version adds a major capability layer.

| Version | Focus | Key Deliverables |
|---------|-------|------------------|
| **V3** | Core research platform | Paper CRUD, arXiv ingestion, hybrid search, AI chat, trending, memory, background workers |
| **V5** | Auth & collaboration | JWT, workspaces, real‑time annotations, shared dashboards |
| **V7** | Collaborative cloud | CRDT sync engine, permission system, shared flashcards, boards |
| **V8** | Literature synthesis | Topic clustering, contradiction detection, citation‑aware reviews, comparison tables |
| **V10** | Autonomous AI scientist | Hypothesis generation, experiment planning, theory comparison, reviewer simulation |
| **V11** | Personalised discovery | Interaction memory, swipe feed, subscription tracking, trending ranker |
| **V12** | Knowledge graph | Neo4j‑compatible property graph, node/edge types, graph visualisation |
| **V13** | Adaptive learning | Concept extraction, prerequisites, mini‑courses, tutoring engine |
| **V14** | Publication workflows | Citation intelligence, reviewer simulation, formatting pipelines |
| **V15** | Research simulation | Predict benchmarks, cost, risk, confidence; rank candidates |
| **V16** | Multimodal understanding | OCR, figure/chart parsing, equation reasoning, table extraction |
| **V17** | Enterprise deployment | Helm, Terraform, SSO, audit logging, multi‑tenancy, SLOs |
| **V18** | Memory & orchestration | Episodic/semantic/procedural memory, agent missions, self‑improvement |

> **Note:** Not all versions are fully implemented in code – some are design docs (`docs/v10/`, `docs/v18/`). The core running system includes V3, V5, V11, V12, V15, V16, and V17.

---

## 📁 Project Directory Structure

```
arxiv-paper-summariser/
├── app/                         # V3 Research API (FastAPI)
│   ├── api/routes/              # Papers, search, chat, feed, memory, ingest
│   ├── core/                    # Config, database, dependencies
│   ├── models/                  # SQLAlchemy models (Paper, PaperChunk, ProcessingJob, etc.)
│   ├── repositories/            # Paper, memory, job repositories
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Embeddings, indexing, search, vector store, arxiv ingestion
│   └── workers/                 # arXiv sync, background job scheduler
├── apps/
│   ├── backend/                 # V5 Auth & Collaboration API
│   │   ├── app/api/v1/          # Login, me, feed, dashboard, graph, chat, annotations, WebSocket
│   │   ├── core/                # Config, security, rate limiting
│   │   └── services/            # Chat, realtime manager, simple repository
│   └── frontend/                # Next.js workspace
│       ├── app/                 # Pages: dashboard, feed, papers/[id], search, trending, graph, workspace, profile
│       ├── components/          # Research shell, command palette, graph canvas, UI primitives
│       ├── lib/                 # API clients (v3, v5)
│       ├── store/               # Zustand stores (bookmarks, session)
│       └── styles/              # Tailwind + custom CSS
├── arxiv-research-copilot/      # Legacy V1 pipeline (single‑paper summarisation)
├── arxiv_paper_summariser_v15/  # Simulation engine (benchmark prediction, workflows)
├── compliance/                  # Audit schema, compliance controls (V17)
├── components/                  # Shared React components (duplicate, but used for static export)
├── deploy/
│   ├── helm/                    # V17 Helm chart (api, worker, autoscaling, tenant quotas)
│   ├── kubernetes/              # Raw K8s manifests (base + production overlay)
│   └── monitoring/              # Prometheus, Alertmanager configs
├── docs/                        # Detailed architecture docs for V4, V6, V7, V10, V12, V14, V17, V18
├── infra/terraform/             # AWS Terraform modules (VPC, EKS, RDS, ElastiCache, S3)
├── lib/                         # Duplicate frontend lib (legacy)
├── migrations/                  # Alembic migrations (V3 database schema)
├── monitoring/                  # Observability stack (Grafana, Loki, Tempo, Prometheus, Alertmanager)
├── policies/                    # Gatekeeper constraint templates (K8s enterprise controls)
├── public/                      # Static assets for frontend
├── research_discovery/          # V11 personalisation engine (feed, memory, ranking)
├── scripts/                     # Deployment, evidence collection, tenant management
├── src/                         # Core research libraries
│   ├── arxiv_copilot/           # V2‑style summarisation pipeline (LLM, chunking, PDF)
│   ├── arxiv_kg_v12/            # Knowledge graph API, extraction, visualisation
│   ├── arxiv_paper_summariser/  # V8–V16 (literature review, concept graph, multimodal, V9 workflow)
│   ├── arxiv_research_copilot_v4/ # V4 agent ecosystem (monitoring, agents, ranking)
│   └── research_cloud/          # V7 collaboration (permissions, shared state, sync engine)
├── store/                       # Duplicate Zustand stores
├── styles/                      # Duplicate global CSS
├── tests/                       # Unit and integration tests (chunking, pipeline, kg, simulation, etc.)
└── .github/workflows/           # CI, GitHub Pages deployment, enterprise CI/CD
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.12+ (for running V3 API outside containers)

### 1. Clone and set up environment

```bash
git clone https://github.com/your-username/arxiv-paper-summariser.git
cd arxiv-paper-summariser
cp .env.example .env
cp .env.local.example apps/frontend/.env.local
```

Edit `.env` with your API keys (Anthropic, OpenAI, Qdrant URL if not using the built‑in memory backend).

### 2. Run with Docker Compose (full stack)

```bash
docker-compose -f docker-compose.dev.yml up
```

This starts:
- PostgreSQL (5432)
- Redis (6379)
- Qdrant (6333)
- V3 API (8000) – with auto‑reload
- V5 API (8001)
- Next.js frontend (3000) – with hot reload

Visit `http://localhost:3000`.

### 3. Ingest your first papers

Use the frontend “Ingest from arXiv” button on the Papers page, or call the API directly:

```bash
curl -X POST "http://localhost:8000/api/v3/ingest/category" \
  -H "Content-Type: application/json" \
  -d '{"category":"cs.AI","max_results":20}'
```

### 4. Search and chat

- Open Search page, type a query (e.g., “attention mechanisms for long sequences”).
- Open a paper detail page, scroll to the chat box, ask questions.

---

## ☁️ Deployment

### Local production‑like (Docker Compose)

```bash
docker-compose up
```

### Kubernetes (Helm)

```bash
helm upgrade --install arxiv-summariser deploy/helm/arxiv-summariser \
  --namespace arxiv-prod --create-namespace \
  --values deploy/helm/arxiv-summariser/values.yaml
```

The Helm chart includes:
- HorizontalPodAutoscaler for API
- KEDA ScaledObject for worker queue scaling
- NetworkPolicy for tenant isolation
- ResourceQuota & LimitRange per tenant

### AWS (Terraform)

```bash
cd infra/terraform
terraform init
terraform plan -var="environment=prod"
terraform apply
```

This provisions VPC, EKS cluster, RDS PostgreSQL (multi‑AZ), ElastiCache Redis, S3 buckets for papers & audit logs, and CloudWatch.

### GitHub Pages (static frontend)

```bash
npm run build   # outputs ./out
npx serve out   # or push to gh-pages branch via GitHub Action
```

---

## 🔌 API Reference

### V3 Research API (`http://localhost:8000/api/v3`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/papers` | List papers (limit, offset, topic filter) |
| POST | `/papers` | Upsert a paper |
| GET | `/paper/{id}` | Get paper by ID |
| PATCH | `/paper/{id}` | Update paper |
| GET | `/search?q=...` | Semantic search (hybrid) |
| GET | `/related/{id}` | Find related papers |
| GET | `/trending` | Trending papers |
| GET | `/feed/personalized` | Personalised feed (user_id, limit) |
| POST | `/chat/paper` | AI chat with a paper (requires `ANTHROPIC_API_KEY`) |
| POST | `/memory/events` | Record a reading/view event |
| GET | `/memory/users/{id}` | Get user profile (interests, topic clusters) |
| POST | `/ingest/category` | Ingest recent papers from an arXiv category |
| POST | `/ingest/paper` | Ingest a single arXiv ID |

### V5 Auth & Collaboration API (`http://localhost:8001/api/v1`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Get JWT token (demo: `founder@arxivcopilot.ai` / `research`) |
| GET | `/me` | Get current user info (Bearer) |
| GET | `/dashboard` | User dashboard stats (Bearer) |
| GET | `/feed` | Public feed (no auth) |
| GET | `/graph` | Knowledge graph nodes/edges (static demo) |
| POST | `/papers/{id}/chat` | Simple chat (mock) with rate limiting |
| WebSocket | `/workspaces/{id}/ws` | Real‑time annotations, presence |

---

## ⚙️ Configuration

Key environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async URL | `postgresql+asyncpg://postgres:postgres@localhost:5432/arxiv_copilot` |
| `REDIS_URL` | Redis URL | `redis://localhost:6379/0` |
| `VECTOR_BACKEND` | `qdrant` or `memory` | `memory` |
| `QDRANT_URL` | Qdrant HTTP URL | `http://localhost:6333` |
| `EMBEDDING_MODEL_NAME` | Sentence‑Transformer model | `sentence-transformers/all-MiniLM-L6-v2` |
| `ANTHROPIC_API_KEY` | For AI chat | (empty) → fallback to heuristic |
| `OPENAI_API_KEY` | For summarisation (fallback) | (empty) |
| `JWT_SECRET` | V5 auth secret | `change-me-in-production` |

For production, also set `FRONTEND_URL`, `QDRANT_API_KEY`, `WORKER_INTERVAL_SECONDS`, etc.

---

## 🧪 Development & Testing

### Backend (V3)

```bash
cd app
pip install -r ../requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend (standalone)

```bash
cd apps/frontend
npm install
npm run dev
```

### Running tests

```bash
# V3 unit tests
pytest tests/

# V4 agent tests
pytest tests/test_v4_workflows.py

# V8 literature review tests
pytest tests/test_v8_literature_review.py

# V9 workflow tests
pytest tests/test_v9_workflow.py

# V12 knowledge graph tests
pytest tests/test_v12_knowledge_graph.py

# V15 simulation tests
pytest tests/test_v15_platform.py

# V16 multimodal tests
pytest tests/test_v16_platform.py

# V7 collaboration tests
pytest tests/test_v7_collaboration.py
```

### Code style

- Python: Black, isort, flake8 (not enforced but recommended)
- TypeScript: ESLint + Prettier (already configured in frontend)

---
Here are all the flowcharts you need to fully explain your project, from high-level architecture down to specific workflows. Each is written in Mermaid syntax and ready to embed in your README or documentation.

---

## 1. High‑Level System Architecture

Shows how users, APIs, workers, storage, AI providers, and external services interact.

```mermaid
flowchart TB
    subgraph Clients
        Web[Next.js Frontend<br/>Port 3000]
        CLI[CLI / Scripts]
    end

    subgraph APIs
        V3[V3 Research API<br/>Port 8000<br/>FastAPI]
        V5[V5 Auth & Collaboration API<br/>Port 8001<br/>FastAPI]
    end

    subgraph Background
        Worker[Background Workers<br/>APScheduler / KEDA]
        Queue[Redis Queue]
    end

    subgraph Storage
        PG[(PostgreSQL<br/>Papers, profiles, jobs)]
        Qdrant[(Qdrant<br/>Vector index, 384d)]
        S3[(S3 / Object Store<br/>PDFs, figures, exports)]
    end

    subgraph AI
        Claude[Anthropic Claude<br/>Paper chat]
        OpenAI[OpenAI‑compatible<br/>Summarisation]
        ST[Sentence‑Transformers<br/>Embeddings]
    end

    subgraph External
        Arxiv[arXiv API]
        Scholar[Semantic Scholar]
    end

    Web --> V3 & V5
    CLI --> V3
    V3 --> PG & Qdrant & Queue
    V5 --> PG
    Worker --> Queue & PG & Qdrant & Claude & OpenAI
    V3 --> ST & Arxiv & Scholar
    V3 & Worker --> S3
```

---

## 2. Data Flow for a Typical User Action (Search + Chat)

Sequence diagram showing how a query becomes results and how a chat request is answered.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant V3_API
    participant V5_API
    participant DB
    participant Qdrant
    participant Claude

    User->>Frontend: Search query
    Frontend->>V3_API: GET /search?q=...
    V3_API->>V3_API: Embed query
    V3_API->>Qdrant: ANN search
    Qdrant-->>V3_API: Top paper IDs
    V3_API->>DB: Fetch paper details
    DB-->>V3_API: Papers
    V3_API-->>Frontend: Search results
    Frontend-->>User: Display papers

    User->>Frontend: Open paper & ask chat
    Frontend->>V3_API: POST /chat/paper
    V3_API->>DB: Get paper metadata
    V3_API->>Claude: Prompt with abstract + question
    Claude-->>V3_API: Answer
    V3_API->>DB: Record memory event
    V3_API-->>Frontend: Answer + citations
    Frontend-->>User: AI response
```

---

## 3. Version Evolution Ladder

Shows how the project grew from V1 to V18, each layer building on the previous.

```mermaid
flowchart LR
    V1[V1: Single‑paper pipeline] --> V2[V2: Structured summaries + flashcards]
    V2 --> V3[V3: Research API, search, chat, memory]
    V3 --> V4[V4: Autonomous agents, monitoring]
    V4 --> V5[V5: Auth, workspaces, real‑time]
    V5 --> V6[V6: Research OS (design)]
    V6 --> V7[V7: Collaboration, CRDT sync]
    V7 --> V8[V8: Literature review synthesis]
    V8 --> V9[V9: Implementation workflow]
    V9 --> V10[V10: Hypothesis & experiment]
    V10 --> V11[V11: Personalised discovery]
    V11 --> V12[V12: Knowledge graph]
    V12 --> V13[V13: Adaptive tutoring]
    V13 --> V14[V14: Publication workflows]
    V14 --> V15[V15: Research simulation]
    V15 --> V16[V16: Multimodal understanding]
    V16 --> V17[V17: Enterprise deployment]
    V17 --> V18[V18: Memory & orchestration]
```

---

## 4. Paper Ingestion Pipeline

From arXiv API to indexed, searchable paper.

```mermaid
flowchart LR
    A[arXiv API] -->|Atom feed| B[Ingestion Service]
    B --> C[Create Paper record]
    C --> D[Extract & chunk text]
    D --> E[Generate embeddings]
    E --> F[Upsert to Qdrant]
    F --> G[Save chunks to DB]
    G --> H[Paper ready for search]
```

---

## 5. Personalised Feed Generation (V11)

How the system mixes subscription, trending, and knowledge‑gap lanes.

```mermaid
graph TD
    User[User] --> Frontend[Next.js Frontend]
    Frontend -->|POST /auth/login| V5_API[V5 API :8001]
    V5_API -->|JWT token| Frontend
    Frontend -->|Bearer token| Dashboard[Dashboard / Workspace]
    Dashboard -->|WebSocket| WS[WebSocket Server]
    WS -->|broadcast annotations| Collaborators[Other users]
    Dashboard -->|POST /workspaces/id/annotations| V5_API
    V5_API -->|store| InMemory[In-memory repository]
    V5_API -->|permission check| RBAC[Role-based access control]
    RBAC -->|owner, admin, editor, viewer| Access[Action allowed or denied]
```

---

## 6. AI Chat with a Paper

How Claude (or fallback) answers questions grounded in paper metadata.

```mermaid
flowchart LR
    User[User question] --> API[V3 Chat API]
    API --> DB[(Paper DB)]
    DB --> |title, abstract, authors, topics| PromptBuilder[Build system prompt]
    PromptBuilder --> Claude[Anthropic Claude]
    Claude --> |answer + citations| API
    API --> User
    API --> Memory[(Record memory event)]
```

---

## 7. Research Simulation Workflow (V15)

Predict outcomes before implementing a new architecture.

```mermaid
flowchart TB
    Arch[ArchitectureSpec] --> Engine[SimulationEngine]
    Exp[ExperimentSpec] --> Engine
    Engine --> Quality[Expected quality score]
    Engine --> Risk[Implementation risk]
    Engine --> Cost[GPU hours & USD cost]
    Engine --> Bench[Benchmark predictions<br/>ROUGE, faithfulness, latency]
    Bench --> Predictor[BenchmarkPredictionSystem]
    Predictor --> |confidence intervals| Plan[ExperimentPlan]
    Plan --> Gates[Acceptance gates]
    Gates --> Decision[Proceed / Revise / Pilot]
```

---

## 8. Multimodal Understanding (V16)

How a PDF asset (figure, equation, table) becomes a structured `UnderstandingResult`.

```mermaid
flowchart LR
    Asset[PaperAsset] --> Router{modality}
    Router -->|figure| Figure[FigureUnderstandingParser]
    Router -->|equation| Equation[EquationReasoningWorkflow]
    Router -->|table| Table[TableExtractionParser]
    Router -->|chart| Chart[ChartReasoningParser]
    Router -->|diagram| Diagram[ArchitectureDiagramParser]
    Router -->|video| Video[VideoUnderstandingParser]

    Figure --> OCR[OCR Pipeline]
    Equation --> OCR
    Table --> OCR
    Chart --> OCR
    Diagram --> OCR
    Video --> OCR

    OCR --> |text, tokens| Result[UnderstandingResult]
    Figure --> Result
    Equation --> Result
    Table --> Result
    Result --> Markdown[Markdown summary]
```

---

## 9. Deployment Architecture (V17 – Kubernetes + Terraform)

Shows how the platform runs in production with multi‑tenancy and observability.

```mermaid
flowchart TB
    subgraph AWS
        VPC[VPC]
        EKS[EKS Cluster]
        RDS[(RDS PostgreSQL<br/>Multi‑AZ)]
        Elasticache[(ElastiCache Redis)]
        S3_Buckets[S3: papers, audit]
    end

    subgraph Kubernetes
        NS_Tenant1[Namespace: tenant-research]
        NS_Tenant2[Namespace: tenant-audit]
        NS_Platform[Namespace: arxiv-platform]
        API[API Deployment<br/>HPA]
        Worker[Worker Deployment<br/>KEDA]
        Ingress[Ingress + cert-manager]
        SSO[OIDC / SSO Proxy]
    end

    subgraph Observability
        Prometheus[Prometheus]
        Loki[Loki]
        Tempo[Tempo]
        Grafana[Grafana]
        Alertmanager[Alertmanager]
    end

    Users --> Ingress
    Ingress --> API & SSO
    API --> RDS & Elasticache & S3_Buckets
    Worker --> RDS & Elasticache & S3_Buckets
    API & Worker --> Prometheus & Loki & Tempo
    Prometheus --> Alertmanager
    Alertmanager --> Slack[PagerDuty / Slack]
```

---

## 10. Real‑Time Collaboration Sync (V7 – CRDT Engine)

How concurrent edits are merged deterministically.

```mermaid
graph LR
    Papers[Paper corpus] --> Extractor[Claim & evidence extraction]
    Extractor --> ClaimGraph[Claim graph]
    ClaimGraph --> TheoryAgent[Theory agent]
    TheoryAgent --> |assumptions, predictions| HypothesisGen[Hypothesis generation]
    HypothesisGen --> |contradiction mining, boundary expansion| Hypothesis[Testable hypothesis]
    Hypothesis --> ExperimentAgent[Experiment agent]
    ExperimentAgent --> |protocol, metrics, falsification| ExperimentPlan[Experiment plan]
    ExperimentPlan --> ReviewerAgent[Reviewer agent]
    ReviewerAgent --> |critique, confidence| RankedHypothesis[Ranked hypothesis]
    RankedHypothesis --> HumanGate[Human approval gate]
    HumanGate --> Execute[Execute experiment]
```

---

## 11. Knowledge Graph Traversal (V12)

Example query: find papers that contradict a given paper.

```mermaid
flowchart LR
    PaperA[Paper A] -->|CONTRADICTS| PaperB[Paper B]
    PaperA -->|CITES| PaperC[Paper C]
    PaperB -->|EVALUATED_ON| DatasetX[Dataset X]
    PaperC -->|USES_METHOD| MethodY[Method Y]
    MethodY -->|IMPROVES| BaselineZ[Baseline Z]

    Query[Find papers that contradict Paper A] --> API[GraphTraversalAPI]
    API --> |walk CONTRADICTS edges| Result[Paper B]
```

---

## 12. Adaptive Tutoring Flow (V13)

How a learner’s message changes the tutoring path.

```mermaid
stateDiagram-v2
    [*] --> Listen: Learner types message
    Listen --> Classify: Check for confusion/mastery markers
    Classify --> Confused: contains "confused", "don't understand"
    Classify --> Mastery: contains "got it", "i know"
    Classify --> Neutral: other
    Confused --> Scaffold: Lower mastery score, give simpler explanation
    Mastery --> Extend: Raise mastery score, give critique question
    Neutral --> Socratic: Ask probing question
    Scaffold --> Quiz: Offer low‑stakes quiz
    Extend --> NextConcept: Advance to next milestone
    Socratic --> Quiz: If mastery still low
    Quiz --> Listen
    NextConcept --> Listen
```

---

## 13. Enterprise CI/CD Pipeline (GitHub Actions + Helm)

How changes flow from commit to production.

```mermaid
graph TD
    Start[Learner starts] --> ModeSelect[Select education mode: Beginner / Undergraduate / Grad / Researcher]
    ModeSelect --> ConceptGraph[Extract concept graph from paper]
    ConceptGraph --> Prerequisites[Identify prerequisites]
    Prerequisites --> Quiz[Generate diagnostic quiz]
    Quiz --> TutorSession[Tutoring session]
    TutorSession --> UserInput[Learner types message]
    UserInput --> Classify{Classify message}
    Classify -->|contains 'confused', 'lost'| LowerConfidence[Lower mastery score]
    LowerConfidence --> Scaffold[Provide scaffolded explanation]
    Scaffold --> OfferQuiz[Offer low-stakes quiz]
    Classify -->|contains 'got it', 'i know'| RaiseConfidence[Raise mastery score]
    RaiseConfidence --> Extend[Give extension / critique question]
    Extend --> NextConcept[Advance to next concept]
    Classify -->|other| Socratic[Ask Socratic question]
    Socratic --> UpdateConfidence[Update confidence based on answer]
    UpdateConfidence --> OfferQuiz
    OfferQuiz --> TutorSession
    NextConcept --> TutorSession
    TutorSession --> |mastery > threshold| Complete[Complete learning path]
```

---

## 14. Background Worker Job Processing

How queued jobs (summarisation, embedding) are consumed.

```mermaid
flowchart LR
    API[V3 API] -->|enqueue job| Queue[Redis Queue]
    Queue --> Worker[Worker process]
    Worker --> |claim next| Job[ProcessingJob]
    Job --> |status=running| Process[Execute task]
    Process --> |full_pipeline| Summarise[Generate summary]
    Process --> |embed/index| Index[Index paper in Qdrant]
    Summarise --> Complete[status=finished]
    Index --> Complete
    Complete --> |update DB| Log[(Job log)]
```

---

## 15. Static Site Generation for Frontend

How the Next.js app becomes a static export for GitHub Pages.

```mermaid
flowchart LR
    Source[Next.js source] --> Build[npm run build]
    Build --> |output: 'export'| OutDir[./out folder]
    OutDir --> GitHub[GitHub Actions]
    GitHub --> |deploy to gh-pages branch| Pages[GitHub Pages]
    Pages --> CDN[CDN / arxivcopilot.github.io]
```

---
## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`feat/amazing-feature`).
3. Commit your changes with clear messages.
4. Add tests for new functionality.
5. Run the test suite.
6. Push and open a Pull Request.

For major changes (new versions, architectural changes), please open an issue first to discuss.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙏 Acknowledgements

- [arXiv](https://arxiv.org) for the open API
- [Anthropic](https://anthropic.com) for Claude
- [Qdrant](https://qdrant.tech) for vector search
- [Sentence‑Transformers](https://sbert.net)
- [FastAPI](https://fastapi.tiangolo.com)
- [Next.js](https://nextjs.org)
- All open‑source contributors whose libraries made this possible.

---

Built by Lalit with the help of his creativity and help from LLMs
```

This README is comprehensive, explains the project’s layered architecture, includes mermaid flowcharts, and serves as both user guide and developer reference. You can place it as `README.md` in the project root.
