# AI-Powered Career Intelligence and Placement Assistant

An enterprise-grade AI platform that helps college students become placement-ready:
resume intelligence, ATS scoring, skill-gap analysis, personalized learning roadmaps,
ML-based placement-probability prediction, embedding-based job matching, and AI-driven
interview/coding/aptitude preparation.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full system design (schema,
API contracts, service boundaries, AI/ML pipeline architecture, deployment topology).

## Status of this codebase

This is a **working, runnable scaffold** implementing all 15 modules end-to-end against
the architecture blueprint — not a UI mockup. What's real today vs. what's a documented
next step:

| Layer | Status |
|---|---|
| Backend (FastAPI, all 16 routers, 42 endpoints) | ✅ Fully implemented |
| Database schema + Alembic migration | ✅ Fully implemented |
| Resume parsing (PDF/DOCX → structured entities) | ✅ Real, rule-based/regex + gazetteer (no LLM dependency) |
| Embeddings + FAISS job matching | ✅ Real, runs locally via `sentence-transformers` (no API key needed) |
| Placement prediction ML model | ✅ Real, trained artifact included (`RandomForest`, ROC-AUC ≈ 0.69 on synthetic data) |
| LLM features (ATS suggestions, roadmap, interview Q&A, coding problem gen) | ✅ Functional today via a **deterministic mock provider** — swap to OpenAI/Gemini via one env var, zero code changes |
| Coding auto-evaluation | ✅ Real subprocess execution with timeout (see production note in `coding/executor.py`) |
| Frontend (React 19 + TS + Vite + Tailwind + ShadCN) | ✅ Builds and type-checks cleanly; all 15 modules have a working page wired to the real API |
| CI/CD (GitHub Actions) | 📋 Not included — see "Next steps" below |
| PDF export for admin analytics | 📋 CSV export works; PDF deferred (see `admin/router.py`) |

## Project Structure

```
career-intel-platform/
├── backend/        FastAPI app, all 15 modules, AI/ML core, Alembic migrations
├── frontend/       React 19 + TypeScript + Vite + Tailwind + ShadCN
├── render.yaml     Render blueprint (MUST stay at repo root — see below)
├── infra/          docker-compose (local dev only), vercel.json reference
├── ml/             notebooks/datasets/pipelines scratch space
└── docs/
    └── ARCHITECTURE.md   Full system design document
```

## Quick Start (local, no Supabase/OpenAI keys required)

The stack is designed to run fully locally with **zero external API keys**:
auth uses a dev-token endpoint, AI features use the deterministic mock LLM provider,
and embeddings run locally via `sentence-transformers`.

### 1. Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# .env defaults already work for local dev (AUTH_MODE=dev, LLM_PROVIDER=mock)

# Start Postgres + Redis (or point DATABASE_URL at your own Postgres instance)
docker compose -f ../infra/docker-compose.yml up -d postgres redis

# Run migrations
alembic upgrade head

# Seed reference data (roles, skill taxonomy, aptitude questions, sample jobs)
PYTHONPATH=. python scripts/seed_data.py

# (Optional) regenerate + retrain the placement model — a trained artifact
# already ships in app/ml_core/artifacts/
PYTHONPATH=. python scripts/generate_synthetic_placement_data.py
PYTHONPATH=. python -m app.ml_core.placement_model.train --data data/placement_training.csv

uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

**Getting a dev token** (since `AUTH_MODE=dev` bypasses real Supabase auth locally):

```bash
curl -X POST http://localhost:8000/api/v1/auth/dev-token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "11111111-1111-1111-1111-111111111111", "email": "student@example.com", "role": "student"}'
```

Use the returned `access_token` as a `Bearer` token for subsequent requests, or wire it
into the frontend's dev flow.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
# For local dev without Supabase, you'll need to adapt src/lib/supabaseClient.ts
# to use the /auth/dev-token flow, or configure a real (free-tier) Supabase project —
# recommended, since it's a 2-minute setup and matches production exactly.
npm run dev
```

Visit `http://localhost:5173`.

### 3. Tests

```bash
cd backend
PYTHONPATH=. pytest tests/unit -v
```

## Switching AI providers (mock → real)

Every LLM-backed feature (ATS suggestions, roadmap generation, interview Q&A/feedback,
coding problem generation) is coded against the `LLMProvider` interface in
`app/ai_core/llm/base.py` — never against a concrete provider. To go live:

```bash
# In backend/.env
LLM_PROVIDER=openai        # or "gemini"
OPENAI_API_KEY=sk-...
```

No other code changes are required — see `app/ai_core/llm/factory.py`.

## Production Deployment

### Backend → Render

**Critical structural rule**: `render.yaml` lives at the **repository root**, not in
`infra/`. Render's "New + → Blueprint" flow only ever looks for it there. If you see
Render fail to detect a backend, a Dockerfile, or a Python entry point, the #1 cause
is `render.yaml` being in the wrong place, or the service's **Root Directory** field
not being set — both are fixed below.

**Option A — Blueprint (uses the included `render.yaml`, recommended)**
1. Push this repo to GitHub with `render.yaml` at the root (already correct in this zip).
2. Render Dashboard → **New + → Blueprint** → select your repo.
3. Render reads `render.yaml`, sees `rootDir: backend`, and builds
   `backend/Dockerfile` using `backend/` as the build context — this is what makes
   the backend folder and its entry point (`app/main.py` → `uvicorn app.main:app`,
   baked into the Dockerfile's `CMD`) actually get found.
4. Fill in the secret env vars Render prompts for (`DATABASE_URL`, `SUPABASE_URL`,
   `SUPABASE_JWT_SECRET`, `SUPABASE_SERVICE_ROLE_KEY`) and click **Apply**.

**Option B — Manual Web Service, no Docker (simplest, fewer moving parts)**
If Docker builds keep failing or timing out on Render's free/starter tier, skip
Docker entirely:
1. Render Dashboard → **New + → Web Service** → connect your repo.
2. **Root Directory**: `backend` ← this is the field that was almost certainly
   left blank or wrong if Render said it couldn't find a backend.
3. **Runtime**: `Python 3`
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Health Check Path**: `/health`
7. Add the same env vars as Option A under the Environment tab.

Either way, verify with:
```bash
curl https://your-backend.onrender.com/health
# {"status": "ok", "service": "...", "environment": "production"}
```
If that 404s, the Root Directory is still wrong — Render is building from repo root
instead of `backend/`.

### Frontend → Vercel
1. Vercel → **Add New → Project** → import the repo.
2. **Root Directory**: `frontend` (Vercel defaults to repo root, which has no
   `package.json` — this is the equivalent mistake to Render's Root Directory issue).
3. Framework preset: Vite (auto-detected via `frontend/vercel.json`).
4. Env vars: `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`.

### Database + Auth + Storage → Supabase
Create a project, run `alembic upgrade head` from `backend/` against its Postgres
connection string (converted to the `postgresql+asyncpg://` scheme), enable Email +
Google providers under Authentication, and create a private Storage bucket named
`resumes`.

### If Render still can't find the backend after Option A or B
This almost always means the **GitHub repo's actual folder layout doesn't match
this zip** — commonly from a double-nested folder created during upload (e.g.
`repo/career-intel-platform/backend/...` instead of `repo/backend/...`). Check by
visiting `https://github.com/<you>/<repo>` in a browser: the root of the file
listing should show `backend/`, `frontend/`, `render.yaml`, `README.md` directly —
not one more folder wrapping all of them. If there's an extra wrapper folder, see
"Re-pushing the corrected structure" below.


## Re-pushing the corrected structure to your existing GitHub repo

If your current repo has a structure mismatch (extra wrapper folder, or
`render.yaml` missing from the root), the cleanest fix is to replace the repo
contents with this corrected zip, from your own machine:

```bash
# 1. Clone your existing repo
git clone https://github.com/aneesroshan16/ai-career-intelligence-placement-assistant.git
cd ai-career-intelligence-placement-assistant

# 2. Wipe everything except .git (keeps your commit history/remote intact)
find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

# 3. Extract this corrected zip's contents directly into the repo root
unzip /path/to/career-intel-platform.zip -d .

# 4. Confirm the layout is now flat at the root
ls
# Expect to see: backend  frontend  infra  docs  ml  render.yaml  README.md  .gitignore

# 5. Commit and push
git add -A
git commit -m "Fix deployment structure: render.yaml at repo root, add .dockerignore"
git push origin main
```

Then redeploy on Render (Manual Deploy → Clear build cache & deploy, or it will
auto-deploy if `autoDeploy: true` picks up the push) and Vercel will auto-redeploy
on push as well.

## Next Steps

- Add GitHub Actions CI (`ruff` + `pytest` for backend, `tsc` + `eslint` for frontend).
- Swap the coding-assessment executor (`app/modules/coding/executor.py`) for a hardened
  sandbox (Judge0 / gVisor / Firecracker) before accepting untrusted submissions at scale.
- Wire PDF export for admin analytics (CSV already works).
- Replace the synthetic placement-outcomes dataset with real (anonymized) cohort data
  once available, and re-run `train.py`.
- Add Playwright/integration tests once a real Supabase project is available in CI.
