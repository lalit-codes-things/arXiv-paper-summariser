# Arxiv Research Copilot V5

A production-grade AI research SaaS for discovering arXiv papers, chatting with papers, collaborating in team workspaces, and visualizing research relationships.

## What is included

- **Frontend:** Next.js app with Tailwind, Framer Motion, shadcn-style primitives, React Query, and Zustand.
- **Backend:** FastAPI API v1 with JWT authentication, user accounts, RBAC, paper chat, research feed, dashboard data, graph data, and workspace websocket updates.
- **Collaboration:** Team workspace model, shared realtime websocket event channel, and authenticated copilot endpoints.
- **Infrastructure:** Dockerfiles, compose, Kubernetes manifests, CI/CD, and Prometheus alerting stubs.

## Local development

```bash
pip install -r apps/backend/requirements.txt
PYTHONPATH=apps/backend uvicorn app.main:app --reload
npm install
npm run dev
```

Demo credentials:

- Email: `founder@arxivcopilot.ai`
- Password: `research`

## API overview

- `POST /api/v1/auth/login` issues JWT access tokens.
- `GET /api/v1/me` returns the authenticated user.
- `GET /api/v1/feed` returns the paper feed.
- `GET /api/v1/dashboard` returns trends, reading stats, saved topics, and recommendations.
- `GET /api/v1/graph` returns interactive paper graph data.
- `POST /api/v1/papers/{paper_id}/chat` answers questions about a paper.
- `WS /api/v1/workspaces/{workspace_id}/ws` streams collaborative workspace updates.

## Production deployment

Use `docker-compose.yml` for a small production-like deployment, or apply the manifests in `deploy/kubernetes` to run frontend and backend deployments behind TLS ingress. Monitoring starter configs live in `deploy/monitoring`.
