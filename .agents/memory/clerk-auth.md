---
name: Clerk auth setup
description: Migrated from Replit Auth (OIDC) to Replit-managed Clerk; key decisions and wiring
---

# Clerk Auth Migration

**Why:** User wanted Google/GitHub/Apple/X OAuth. Replit Auth only supports "Sign in with Replit". Migration from Replit Auth → Clerk is not supported by automated tools, so it was done manually.

## What was removed (Replit Auth)
- `artifacts/api-server/src/lib/auth.ts` — OIDC session helpers (kept in repo but unused)
- `artifacts/api-server/src/middlewares/authMiddleware.ts` — old OIDC middleware (kept, unused)
- `artifacts/api-server/src/routes/auth.ts` — /login /callback /logout routes (kept, unused)
- `@workspace/replit-auth-web` package — no longer imported anywhere

## What was added (Clerk)
- `@clerk/express`, `@clerk/shared`, `http-proxy-middleware` on api-server
- `@clerk/react`, `@clerk/themes` on arxiv-copilot
- `artifacts/api-server/src/middlewares/clerkProxyMiddleware.ts` — copied from template
- `artifacts/arxiv-copilot/public/logo.svg` — custom branded logo for Clerk sign-in page

## Critical wiring (must not change)
- `publishableKeyFromHost(window.location.hostname, VITE_CLERK_PUBLISHABLE_KEY)` from `@clerk/react/internal` — never the raw env var
- `clerkProxyUrl = import.meta.env.VITE_CLERK_PROXY_URL` — unconditional, empty in dev (intentional)
- Routes MUST be `/sign-in/*?` and `/sign-up/*?` — the `/*?` optional wildcard is required
- `tailwindcss({ optimize: false })` in vite.config.ts — required for Clerk CSS layer ordering in prod
- `@layer theme, base, clerk, components, utilities;` before `@import 'tailwindcss'` in index.css

## How to add more OAuth providers
Go to the Auth pane (shield icon) in the Replit workspace toolbar. No code changes needed.

## User identity (Clerk)
- `useUser()` from `@clerk/react` → `{ user, isLoaded, isSignedIn }`
- `user.firstName`, `user.lastName`, `user.emailAddresses[0].emailAddress`, `user.imageUrl`
- `useClerk()` → `{ signOut }` — call `signOut({ redirectUrl: basePath || '/' })`
- Do NOT use `useAuth()` from `@workspace/replit-auth-web` anywhere
