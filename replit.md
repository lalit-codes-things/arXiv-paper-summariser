# Arxiv Copilot

AI-powered research platform for searching, reading, and discussing arXiv papers with semantic embeddings, personalized ranking, and team collaboration.

## Run & Operate

- `pnpm --filter @workspace/arxiv-copilot run dev` — run the frontend (via workflow)
- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- Frontend: React + Vite + Tailwind v4 + wouter (routing) + Tanstack Query + Zustand
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- Build: esbuild (CJS bundle)

## Where things live

- `artifacts/arxiv-copilot/` — React + Vite frontend (routes at `/`)
- `artifacts/api-server/` — Express backend (routes at `/api`)
- `artifacts/arxiv-copilot/src/pages/` — page components (one per route)
- `artifacts/arxiv-copilot/src/components/research/` — shell, command palette, graph canvas
- `artifacts/arxiv-copilot/src/lib/api.ts` — typed API clients (v3 and v5 backends)
- `artifacts/arxiv-copilot/src/store/` — Zustand stores (session, bookmarks)

## Architecture decisions

- The app calls two external Python backends: `v3` (port 8000) and `v5` (port 8001), configured via `VITE_V3_API_URL` and `VITE_V5_API_URL` env vars. These default to localhost URLs and will show empty state without the backends running.
- Routing uses wouter (already in the scaffold) instead of react-router.
- Tailwind v4 with inline CSS theme — no separate `tailwind.config.ts` needed; `@tailwindcss/vite` handles it.
- Dark-only theme; the grid background, glass cards, and glow shadow are custom CSS utilities in `src/index.css`.

## Product

- Home page with feature overview
- Dashboard with reading stats, trending topics, recommended papers
- Personalized feed ranked by relevance
- Semantic + hybrid search
- Papers browser with topic filtering and arXiv ingest
- Paper detail with AI chat, related papers, bookmarking
- Trending papers leaderboard
- Knowledge graph visualization
- Team workspace with collaborative summaries
- Research profile with topic clusters
- Login page for v5 API authentication
- ⌘K command palette for quick search

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- Do NOT run `pnpm dev` at workspace root — use workflows or `pnpm --filter @workspace/<slug> run dev`.
- The external Python backends (v3/v5) are not part of this repo; the UI shows empty state gracefully when they're offline.
- `VITE_` prefix required for env vars (not `NEXT_PUBLIC_`).

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
