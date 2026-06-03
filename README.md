# arXiv Paper Summariser

<p align="center">
  <a href="https://lalit-codes-things.github.io/arXiv-paper-summariser/">
    <img alt="Live Demo" src="https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-2ea44f?style=for-the-badge" />
  </a>
</p>

The repository root is now the Next.js frontend. GitHub Pages builds the static site directly from the root and publishes the generated `out/` folder to the `gh-pages` branch.

## Live demo

Visit the deployed app:

**https://lalit-codes-things.github.io/arXiv-paper-summariser/**

## Local development

```bash
npm ci
npm run dev
```

Open http://localhost:3000.

## Static build

```bash
npm ci
npm run build
npm run preview
```

The static export is written to `out/`.

## GitHub Pages deployment

The workflow at `.github/workflows/deploy.yml` deploys automatically on pushes to `main`:

1. Checks out the repository.
2. Runs `npm ci`.
3. Runs `npm run build` with `GITHUB_PAGES=true`.
4. Publishes `out/` to the `gh-pages` branch with `peaceiris/actions-gh-pages`.

## GitHub Pages settings

In GitHub, configure:

1. Go to **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Set **Branch** to `gh-pages`.
4. Set the folder to `/ (root)`.
5. Save.

After the deploy workflow completes, GitHub Pages serves the app from:

```text
https://lalit-codes-things.github.io/arXiv-paper-summariser/
```

## Frontend structure

```text
app/                  Next.js App Router pages plus existing Python API package
components/           Shared React components
lib/                  Frontend API helpers and utilities
store/                Zustand stores
styles/               Global CSS
public/               Static public assets
out/                  Generated static export (created by npm run build)
```

## Final deployment steps

```bash
git add .
git commit -m "Flatten frontend for GitHub Pages static export"
git push origin main
```

Then enable GitHub Pages with the settings above and wait for the `Deploy GitHub Pages` workflow to publish `gh-pages`.
