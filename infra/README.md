# Why render.yaml isn't in this folder

`render.yaml` **must live at the repository root** — Render's "New + → Blueprint"
flow only auto-detects it there, never inside a subfolder like `infra/`. It's at
`../render.yaml` (repo root). This file exists just to explain the move for anyone
who goes looking for it here.

`vercel.json` in this folder is a reference copy only. The one Vercel actually
reads is `frontend/vercel.json`, because your Vercel project's **Root Directory**
setting is `frontend` — Vercel looks for `vercel.json` relative to that root.

`docker-compose.yml` here is for **local development only** (spins up Postgres +
Redis + the backend container on your machine). It is not used by Render or
Vercel in production.
