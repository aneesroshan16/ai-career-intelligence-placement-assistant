# AI-Powered Career Intelligence and Placement Assistant
## System Architecture Blueprint (v1.0)

**Status:** Design phase — foundation for module-by-module implementation
**Target:** Final-year AI & Data Science major project / portfolio-grade production system

---

## 1. System Overview

### 1.1 Architectural Style
A **modular monolith** on the backend (single FastAPI codebase, strictly separated modules with internal service boundaries) rather than microservices. Rationale for a portfolio/production project of this size:

- Easier to deploy on Render's free/hobby tiers (one service, not 10).
- Module boundaries are enforced at the *code* level (routers → services → repositories), so it can be split into microservices later without a rewrite — each module already owns its own service layer and DB access pattern.
- Shared DB session, shared auth middleware, shared caching layer — avoids distributed-systems complexity that isn't justified at this scale.

The **ML/AI subsystem** is isolated behind a service interface (`ai_core/`) so inference logic (mock today, real LLM/embeddings tomorrow) never leaks into route handlers.

### 1.2 High-Level Component Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER (Vercel)                        │
│  React 19 + TS + Vite + Tailwind + ShadCN + React Router + Recharts  │
│  - Student Dashboard   - Admin Dashboard   - Analytics Dashboard      │
│  - Auth (Supabase JS)  - Resume Upload UI  - Interview Simulator UI   │
└───────────────────────────────┬────────────────────────────────────┘
                                 │ HTTPS (JWT Bearer)
┌───────────────────────────────▼────────────────────────────────────┐
│                     API GATEWAY LAYER (FastAPI, Render)              │
│  Middleware: CORS, Auth (JWT verify), Rate Limiting, Logging,        │
│              Request ID, Error Handler, Response Cache                │
├────────────────────────────────────────────────────────────────────┤
│                         ROUTER LAYER (/api/v1/*)                     │
│  auth · users · resumes · ats · skills · roadmap · readiness ·       │
│  placement · matching · interview · coding · aptitude · jobs ·       │
│  dashboard · admin · analytics                                       │
├────────────────────────────────────────────────────────────────────┤
│                         SERVICE LAYER (business logic)                │
│  Each module = service class, pure Python, framework-agnostic         │
├──────────────────────────┬─────────────────────────┬─────────────────┤
│   AI CORE (ai_core/)     │   ML CORE (ml_core/)     │  REPOSITORY LAYER │
│  - LLM Provider Interface│  - Placement Predictor   │  SQLAlchemy 2.0   │
│    (Mock/OpenAI/Gemini)  │    (XGBoost/CatBoost/RF) │  async ORM        │
│  - Embedding Provider    │  - Feature Engineering   │  repositories per │
│    (SentenceTransformers)│  - Model Registry        │  aggregate root   │
│  - Resume Parser (NLP)   │  - Training Pipeline     │                  │
│  - Interview Feedback Gen│  - Model Versioning       │                  │
│  - Vector Store (FAISS)  │                          │                  │
└──────────────────────────┴─────────────────────────┴─────────────────┘
                                 │
┌────────────────────────────────▼───────────────────────────────────┐
│                          DATA LAYER (Supabase)                       │
│  PostgreSQL (primary DB)  ·  Supabase Auth (identity)  ·             │
│  Supabase Storage (resume PDFs/DOCX, reports)  ·  Redis (cache, opt.) │
└────────────────────────────────────────────────────────────────────┘
```

### 1.3 Request Lifecycle (example: resume upload)
1. Client uploads file → `POST /api/v1/resumes` with JWT.
2. Auth middleware verifies Supabase JWT, injects `current_user` into request scope.
3. Rate limiter checks per-user quota (slowapi + Redis/in-memory).
4. Router delegates to `ResumeService.process_upload()`.
5. Service stores raw file in Supabase Storage, persists `Resume` row (status=`processing`).
6. Service calls `ai_core.resume_parser.parse()` → structured JSON (skills, education, projects, certs).
7. Service persists parsed entities (`Skill`, `Education`, `Project`, `Certification` rows linked to resume).
8. Background task (FastAPI `BackgroundTasks` or Celery-lite) triggers ATS scoring + embedding generation.
9. Response returns resume ID + status immediately (async processing pattern); client polls or receives websocket/SSE update.

---

## 2. Service Boundaries (Module → Owned Responsibility)

| # | Module | Owns | Depends On |
|---|--------|------|------------|
| 1 | Auth | Session validation, RBAC, profile bootstrap | Supabase Auth |
| 2 | Resume | Upload, storage, parsing orchestration | AI Core (parser), Storage |
| 3 | ATS Analyzer | Scoring rules, keyword match, formatting checks | Resume module, AI Core |
| 4 | Skill Gap | Role skill taxonomies, gap computation | Resume module |
| 5 | Roadmap | Weekly/monthly plan generation | Skill Gap, AI Core (LLM) |
| 6 | Readiness Scoring | Aggregates sub-scores into composite score | ATS, Coding, Aptitude, Interview |
| 7 | Placement Prediction | ML inference on tabular features | ML Core |
| 8 | Job Matching | Embedding similarity resume↔job | AI Core (embeddings), FAISS |
| 9 | Interview Simulator | Question generation, transcript, feedback | AI Core (LLM) |
| 10 | Coding Assessment | Problem generation, auto-eval (test-case runner) | AI Core (LLM), sandboxed exec |
| 11 | Aptitude Assessment | Question bank, scoring | Static question bank (seeded) |
| 12 | Job Recommendation | Filter/rank job postings | Job Matching, Jobs table |
| 13 | Student Dashboard | Read-aggregation across modules 3,4,6,7,9 | All of the above (read-only) |
| 14 | Admin Dashboard | Department/cohort aggregation, exports | All modules (read-only, scoped) |
| 15 | Analytics | Cross-cohort trends, skill demand | Jobs, Placement, Skill Gap |

Each module is a Python package: `app/modules/<module_name>/{router.py, service.py, schemas.py, models.py, repository.py}`.

---

## 3. Folder Structure

### 3.1 Monorepo Layout
```
career-intel-platform/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app factory
│   │   ├── core/
│   │   │   ├── config.py                # Pydantic Settings (env vars)
│   │   │   ├── security.py              # JWT verify, password/RBAC helpers
│   │   │   ├── database.py              # Async SQLAlchemy engine/session
│   │   │   ├── logging.py               # Structured logging (structlog)
│   │   │   ├── cache.py                 # Redis/in-memory cache wrapper
│   │   │   ├── rate_limit.py            # slowapi limiter config
│   │   │   ├── exceptions.py            # Custom exception classes
│   │   │   └── middleware.py            # Request ID, error handler, CORS
│   │   ├── modules/
│   │   │   ├── auth/
│   │   │   ├── users/
│   │   │   ├── resumes/
│   │   │   ├── ats/
│   │   │   ├── skills/                  # skill gap analysis
│   │   │   ├── roadmap/
│   │   │   ├── readiness/
│   │   │   ├── placement/               # ML prediction
│   │   │   ├── matching/                # job matching engine
│   │   │   ├── interview/
│   │   │   ├── coding/
│   │   │   ├── aptitude/
│   │   │   ├── jobs/                    # recommendation
│   │   │   ├── dashboard/
│   │   │   ├── admin/
│   │   │   └── analytics/
│   │   │   (each: router.py, service.py, schemas.py, models.py, repository.py, __init__.py)
│   │   ├── ai_core/
│   │   │   ├── llm/
│   │   │   │   ├── base.py              # Abstract LLMProvider interface
│   │   │   │   ├── mock_provider.py     # Deterministic mock responses
│   │   │   │   ├── openai_provider.py   # Real OpenAI impl (stub today)
│   │   │   │   └── gemini_provider.py   # Real Gemini impl (stub today)
│   │   │   ├── embeddings/
│   │   │   │   ├── base.py
│   │   │   │   └── sentence_transformer_provider.py
│   │   │   ├── resume_parser/
│   │   │   │   ├── extractor.py         # PDF/DOCX text extraction
│   │   │   │   ├── ner_pipeline.py      # spaCy/regex hybrid extraction
│   │   │   │   └── schema.py
│   │   │   ├── vector_store/
│   │   │   │   └── faiss_store.py
│   │   │   └── prompts/                 # versioned prompt templates
│   │   ├── ml_core/
│   │   │   ├── placement_model/
│   │   │   │   ├── features.py
│   │   │   │   ├── train.py
│   │   │   │   ├── predict.py
│   │   │   │   └── registry.py          # model version registry
│   │   │   └── artifacts/               # saved .pkl/.cbm/.json models
│   │   └── shared/
│   │       ├── enums.py
│   │       ├── pagination.py
│   │       └── base_schemas.py
│   ├── alembic/                         # DB migrations
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── scripts/
│   │   ├── seed_data.py
│   │   └── train_models.py
│   ├── data/                            # sample datasets
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── routes/                      # React Router route tree
│   │   ├── pages/
│   │   │   ├── auth/
│   │   │   ├── student/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── ResumeUpload.tsx
│   │   │   │   ├── SkillGap.tsx
│   │   │   │   ├── Roadmap.tsx
│   │   │   │   ├── Interview.tsx
│   │   │   │   ├── CodingTest.tsx
│   │   │   │   ├── Aptitude.tsx
│   │   │   │   └── Jobs.tsx
│   │   │   ├── admin/
│   │   │   └── analytics/
│   │   ├── components/
│   │   │   ├── ui/                      # ShadCN primitives
│   │   │   ├── charts/                  # Recharts wrappers
│   │   │   ├── layout/                  # Shell, Sidebar, Navbar, ThemeToggle
│   │   │   └── shared/
│   │   ├── lib/
│   │   │   ├── api/                     # typed API client per module
│   │   │   ├── supabaseClient.ts
│   │   │   ├── queryClient.ts           # TanStack Query setup
│   │   │   └── utils.ts
│   │   ├── hooks/
│   │   ├── store/                       # Zustand (auth/theme state)
│   │   ├── types/                       # shared TS types (mirrors backend schemas)
│   │   └── styles/
│   ├── public/
│   ├── index.html
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   └── package.json
├── ml/
│   ├── notebooks/                       # EDA, model experimentation
│   ├── datasets/                        # raw/processed training data
│   └── pipelines/                       # standalone training scripts
├── infra/
│   ├── docker-compose.yml               # local dev: backend+db+redis
│   ├── render.yaml                      # Render deployment blueprint
│   └── vercel.json
├── docs/
│   ├── ARCHITECTURE.md                  # this file
│   ├── API.md                           # generated/curated API contracts
│   └── ERD.png
└── README.md
```

---

## 4. Database Schema (PostgreSQL)

### 4.1 Entity Relationship Summary
```
users ──1:1── student_profiles ──1:N── resumes ──1:N── resume_skills
  │                                        │              │
  │                                        ├─1:N── resume_education
  │                                        ├─1:N── resume_projects
  │                                        └─1:N── resume_certifications
  │
  ├─1:N── ats_reports (fk resume_id)
  ├─1:N── skill_gap_reports (fk resume_id, role_id)
  ├─1:N── roadmaps (fk skill_gap_report_id)
  ├─1:N── readiness_scores
  ├─1:N── placement_predictions
  ├─1:N── job_matches (fk resume_id, job_id)
  ├─1:N── interview_sessions ──1:N── interview_turns
  ├─1:N── coding_attempts (fk problem_id)
  └─1:N── aptitude_attempts

roles (target job roles: Data Scientist, ML Engineer, ...) ──1:N── role_skills
jobs ──N:1── companies
jobs ──1:N── job_matches
coding_problems ──1:N── coding_attempts
aptitude_questions ──1:N── aptitude_answers
departments ──1:N── student_profiles   (for admin analytics)
```

### 4.2 DDL (core tables)

```sql
-- ============ IDENTITY ============
CREATE TABLE users (
    id              UUID PRIMARY KEY,              -- mirrors Supabase auth.users.id
    email           TEXT UNIQUE NOT NULL,
    full_name       TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student','admin','placement_officer')),
    avatar_url      TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE departments (
    id              SERIAL PRIMARY KEY,
    name            TEXT UNIQUE NOT NULL,           -- e.g. 'CSE', 'AI&DS', 'ECE'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE student_profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    roll_number     TEXT UNIQUE,
    department_id   INTEGER REFERENCES departments(id),
    graduation_year INTEGER,
    cgpa            NUMERIC(4,2),
    internships     INTEGER NOT NULL DEFAULT 0,
    active_backlogs INTEGER NOT NULL DEFAULT 0,
    phone           TEXT,
    location        TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ ROLES / SKILL TAXONOMY ============
CREATE TABLE roles (
    id              SERIAL PRIMARY KEY,
    name            TEXT UNIQUE NOT NULL             -- Data Scientist, Data Analyst, ML Engineer, Software Engineer, AI Engineer
);

CREATE TABLE skills_master (
    id              SERIAL PRIMARY KEY,
    name            TEXT UNIQUE NOT NULL,
    category        TEXT                             -- language, framework, tool, soft-skill, domain
);

CREATE TABLE role_skills (
    id              SERIAL PRIMARY KEY,
    role_id         INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    skill_id        INTEGER NOT NULL REFERENCES skills_master(id) ON DELETE CASCADE,
    importance      SMALLINT NOT NULL DEFAULT 3 CHECK (importance BETWEEN 1 AND 5),
    UNIQUE(role_id, skill_id)
);

-- ============ RESUME ============
CREATE TABLE resumes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_url        TEXT NOT NULL,                   -- Supabase Storage path
    file_type       TEXT NOT NULL CHECK (file_type IN ('pdf','docx')),
    original_filename TEXT NOT NULL,
    parse_status    TEXT NOT NULL DEFAULT 'pending' CHECK (parse_status IN ('pending','processing','completed','failed')),
    raw_text        TEXT,
    embedding_id    TEXT,                            -- FAISS vector id reference
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,    -- latest resume flag
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE resume_skills (
    id              SERIAL PRIMARY KEY,
    resume_id       UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    skill_id        INTEGER REFERENCES skills_master(id),
    raw_text        TEXT NOT NULL,                    -- as extracted, pre-normalization
    proficiency     TEXT CHECK (proficiency IN ('beginner','intermediate','advanced'))
);

CREATE TABLE resume_education (
    id              SERIAL PRIMARY KEY,
    resume_id       UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    institution     TEXT,
    degree          TEXT,
    field_of_study  TEXT,
    start_year      INTEGER,
    end_year        INTEGER,
    gpa             NUMERIC(4,2)
);

CREATE TABLE resume_projects (
    id              SERIAL PRIMARY KEY,
    resume_id       UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    description     TEXT,
    tech_stack      TEXT[],
    project_url     TEXT
);

CREATE TABLE resume_certifications (
    id              SERIAL PRIMARY KEY,
    resume_id       UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    title           TEXT NOT NULL,
    issuer          TEXT,
    issue_date      DATE,
    credential_url  TEXT
);

-- ============ ATS ============
CREATE TABLE ats_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id       UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    overall_score   NUMERIC(5,2) NOT NULL,            -- 0-100
    keyword_score   NUMERIC(5,2),
    formatting_score NUMERIC(5,2),
    section_score   NUMERIC(5,2),
    missing_sections TEXT[],
    suggestions     JSONB,                            -- list of {issue, recommendation, severity}
    target_role_id  INTEGER REFERENCES roles(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ SKILL GAP + ROADMAP ============
CREATE TABLE skill_gap_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id       UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    role_id         INTEGER NOT NULL REFERENCES roles(id),
    matched_skills  JSONB NOT NULL,                   -- [{skill, importance}]
    missing_skills  JSONB NOT NULL,                   -- [{skill, importance}]
    match_percentage NUMERIC(5,2) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE roadmaps (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_gap_report_id UUID NOT NULL REFERENCES skill_gap_reports(id) ON DELETE CASCADE,
    total_weeks     INTEGER NOT NULL,
    plan            JSONB NOT NULL,                   -- [{week, focus_skills, tasks[], est_hours}]
    milestones      JSONB NOT NULL,                   -- [{month, goal, deliverable}]
    generated_by    TEXT NOT NULL DEFAULT 'mock',      -- 'mock' | 'openai' | 'gemini'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ READINESS + PLACEMENT PREDICTION ============
CREATE TABLE readiness_scores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    technical_score NUMERIC(5,2),
    aptitude_score  NUMERIC(5,2),
    communication_score NUMERIC(5,2),
    interview_score NUMERIC(5,2),
    overall_score   NUMERIC(5,2) NOT NULL,
    computed_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE placement_predictions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model_version   TEXT NOT NULL,
    input_features  JSONB NOT NULL,                   -- snapshot of features used
    probability     NUMERIC(5,4) NOT NULL,             -- 0.0000-1.0000
    predicted_label BOOLEAN,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ JOBS + MATCHING ============
CREATE TABLE companies (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    logo_url        TEXT
);

CREATE TABLE jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      INTEGER REFERENCES companies(id),
    title           TEXT NOT NULL,
    role_id         INTEGER REFERENCES roles(id),
    description     TEXT,
    required_skills JSONB,
    experience_min  NUMERIC(3,1) DEFAULT 0,
    experience_max  NUMERIC(3,1),
    location        TEXT,
    job_type        TEXT CHECK (job_type IN ('internship','full_time','contract')),
    embedding_id    TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    posted_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE job_matches (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id       UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    job_id          UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    similarity_score NUMERIC(5,4) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(resume_id, job_id)
);

-- ============ INTERVIEW SIMULATOR ============
CREATE TABLE interview_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mode            TEXT NOT NULL CHECK (mode IN ('hr','technical')),
    role_id         INTEGER REFERENCES roles(id),
    status          TEXT NOT NULL DEFAULT 'in_progress' CHECK (status IN ('in_progress','completed','abandoned')),
    overall_feedback JSONB,
    score           NUMERIC(5,2),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ
);

CREATE TABLE interview_turns (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    turn_number     INTEGER NOT NULL,
    question        TEXT NOT NULL,
    answer          TEXT,
    feedback        JSONB,                            -- {clarity, correctness, confidence, tips[]}
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ CODING ASSESSMENT ============
CREATE TABLE coding_problems (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id         INTEGER REFERENCES roles(id),
    title           TEXT NOT NULL,
    difficulty      TEXT CHECK (difficulty IN ('easy','medium','hard')),
    statement       TEXT NOT NULL,
    starter_code    JSONB,                            -- {python: "...", javascript: "..."}
    test_cases      JSONB NOT NULL,                   -- [{input, expected_output, hidden}]
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE coding_attempts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    problem_id      UUID NOT NULL REFERENCES coding_problems(id),
    submitted_code  TEXT NOT NULL,
    language        TEXT NOT NULL,
    passed_cases    INTEGER NOT NULL DEFAULT 0,
    total_cases     INTEGER NOT NULL DEFAULT 0,
    score           NUMERIC(5,2),
    execution_log   JSONB,
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ APTITUDE ASSESSMENT ============
CREATE TABLE aptitude_questions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category        TEXT NOT NULL CHECK (category IN ('quantitative','logical','verbal')),
    question        TEXT NOT NULL,
    options         JSONB NOT NULL,                   -- ["A","B","C","D"]
    correct_option  SMALLINT NOT NULL,
    difficulty      TEXT CHECK (difficulty IN ('easy','medium','hard'))
);

CREATE TABLE aptitude_attempts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_scores JSONB NOT NULL,                   -- {quantitative: 80, logical: 65, verbal: 70}
    overall_score   NUMERIC(5,2) NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ INDEXES ============
CREATE INDEX idx_resumes_user ON resumes(user_id);
CREATE INDEX idx_resume_skills_resume ON resume_skills(resume_id);
CREATE INDEX idx_ats_reports_resume ON ats_reports(resume_id);
CREATE INDEX idx_skill_gap_resume_role ON skill_gap_reports(resume_id, role_id);
CREATE INDEX idx_placement_pred_user ON placement_predictions(user_id);
CREATE INDEX idx_job_matches_resume ON job_matches(resume_id);
CREATE INDEX idx_jobs_role ON jobs(role_id);
CREATE INDEX idx_interview_sessions_user ON interview_sessions(user_id);
CREATE INDEX idx_coding_attempts_user ON coding_attempts(user_id);
CREATE INDEX idx_student_profiles_dept ON student_profiles(department_id);
```

Migrations are managed via **Alembic**; the above DDL is the target state for the initial migration (`0001_init.py`).

---

## 5. Authentication & Authorization Design

### 5.1 Identity Provider
**Supabase Auth** is the source of truth for identity (email/password + Google OAuth). The FastAPI backend does **not** issue its own passwords — it verifies Supabase-issued JWTs.

### 5.2 Flow
1. Frontend uses `@supabase/supabase-js` for signup/login/Google OAuth → receives a Supabase session JWT (RS256, verifiable via Supabase's JWKS endpoint).
2. Frontend attaches `Authorization: Bearer <jwt>` to every API call.
3. FastAPI middleware (`core/security.py`) verifies the JWT signature against Supabase's public JWKS (cached, refreshed periodically), extracts `sub` (user id) and `email`.
4. On first authenticated request, backend **lazily provisions** a `users` row (upsert on `id`) — no separate registration endpoint needed on the backend side.
5. `role` (student/admin/placement_officer) is stored in `users.role` (backend-owned, not in the JWT) — checked via a `require_role(["admin"])` FastAPI dependency for RBAC.

### 5.3 RBAC Matrix

| Endpoint group | student | placement_officer | admin |
|---|---|---|---|
| `/resumes/*`, `/ats/*`, `/skills/*`, `/roadmap/*` (own data) | ✅ | ✅ (read) | ✅ (read) |
| `/interview/*`, `/coding/*`, `/aptitude/*` (own data) | ✅ | ✅ (read) | ✅ (read) |
| `/dashboard/*` (own) | ✅ | ❌ | ❌ |
| `/admin/*` (cohort/dept aggregation, exports) | ❌ | ✅ | ✅ |
| `/analytics/*` | ❌ | ✅ | ✅ |
| `/jobs` (CRUD postings) | ❌ (read-only) | ✅ | ✅ |

### 5.4 Security Middleware Stack (applied in order)
`CORS → RequestID → RateLimiter (slowapi) → JWTAuth → RoleGuard (per-route) → ErrorHandler → Router`

---

## 6. API Contracts (REST, `/api/v1` prefix)

Full OpenAPI/Swagger is auto-generated by FastAPI at `/docs`; below is the curated contract surface per module.

### 6.1 Auth & Users
| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/users/me` | Get current user + profile | Any |
| PUT | `/users/me` | Update profile (cgpa, dept, internships...) | Any |
| GET | `/users/{id}` | Admin: fetch any student profile | admin |

### 6.2 Resumes
| Method | Path | Description |
|---|---|---|
| POST | `/resumes` | Upload PDF/DOCX (multipart) → triggers parse pipeline |
| GET | `/resumes` | List user's resumes |
| GET | `/resumes/{id}` | Get resume detail incl. parsed entities |
| GET | `/resumes/{id}/status` | Poll parse status |
| DELETE | `/resumes/{id}` | Soft-delete resume |

### 6.3 ATS Analyzer
| Method | Path | Description |
|---|---|---|
| POST | `/ats/analyze` | Body: `{resume_id, target_role_id}` → generates report |
| GET | `/ats/reports/{resume_id}` | Latest report for a resume |
| GET | `/ats/reports/{resume_id}/history` | Score trend over time |

### 6.4 Skill Gap
| Method | Path | Description |
|---|---|---|
| POST | `/skills/gap-analysis` | Body: `{resume_id, role_id}` → matched/missing skills |
| GET | `/skills/roles` | List supported target roles |
| GET | `/skills/gap-analysis/{id}` | Fetch a saved report |

### 6.5 Roadmap
| Method | Path | Description |
|---|---|---|
| POST | `/roadmap/generate` | Body: `{skill_gap_report_id, weeks}` |
| GET | `/roadmap/{id}` | Fetch roadmap |
| PATCH | `/roadmap/{id}/progress` | Mark tasks complete |

### 6.6 Readiness Scoring
| Method | Path | Description |
|---|---|---|
| GET | `/readiness/me` | Latest composite readiness score |
| POST | `/readiness/recompute` | Force recompute from latest sub-scores |
| GET | `/readiness/me/history` | Trend for dashboard chart |

### 6.7 Placement Prediction
| Method | Path | Description |
|---|---|---|
| POST | `/placement/predict` | Body: features (cgpa, internships, projects, certs, skills_count, coding_score, aptitude_score) → `{probability, label, model_version}` |
| GET | `/placement/predict/history` | Past predictions |

### 6.8 Job Matching & Recommendation
| Method | Path | Description |
|---|---|---|
| POST | `/matching/compute` | Body: `{resume_id}` → recompute embeddings vs all active jobs |
| GET | `/matching/{resume_id}` | Ranked match list |
| GET | `/jobs` | List/filter jobs (`?location=&job_type=&experience_max=&role_id=`) |
| GET | `/jobs/{id}` | Job detail |
| POST | `/jobs` | Create posting (admin/placement_officer) |
| GET | `/jobs/recommended` | Personalized recommendations for current user |

### 6.9 Interview Simulator
| Method | Path | Description |
|---|---|---|
| POST | `/interview/sessions` | Body: `{mode, role_id}` → starts session, returns first question |
| POST | `/interview/sessions/{id}/answer` | Body: `{answer}` → returns feedback + next question |
| POST | `/interview/sessions/{id}/complete` | Finalizes session, aggregate feedback |
| GET | `/interview/sessions` | History list |
| GET | `/interview/sessions/{id}` | Full transcript |

### 6.10 Coding Assessment
| Method | Path | Description |
|---|---|---|
| POST | `/coding/generate` | Body: `{role_id, difficulty}` → new problem |
| POST | `/coding/{problem_id}/submit` | Body: `{code, language}` → runs against test cases, returns score |
| GET | `/coding/attempts` | History |

### 6.11 Aptitude Assessment
| Method | Path | Description |
|---|---|---|
| GET | `/aptitude/test` | Fetch a generated test (N questions per category) |
| POST | `/aptitude/submit` | Body: `{answers: [{question_id, selected_option}]}` → scored result |
| GET | `/aptitude/attempts` | History |

### 6.12 Dashboards & Analytics
| Method | Path | Description |
|---|---|---|
| GET | `/dashboard/student` | Aggregated payload: ATS trend, readiness trend, skill progress, interview history |
| GET | `/admin/analytics/department` | Per-department placement stats |
| GET | `/admin/analytics/export` | CSV/PDF export (`?format=csv|pdf`) |
| GET | `/analytics/skill-demand` | Aggregated in-demand skills across job postings |
| GET | `/analytics/placement-trends` | Cohort-wide predicted vs actual placement trends |

### 6.13 Standard Response Envelope
```json
{
  "success": true,
  "data": { "...": "..." },
  "meta": { "request_id": "uuid", "timestamp": "iso8601" },
  "error": null
}
```
Errors:
```json
{
  "success": false,
  "data": null,
  "meta": { "request_id": "uuid", "timestamp": "iso8601" },
  "error": { "code": "RESUME_PARSE_FAILED", "message": "...", "details": {} }
}
```

---

## 7. AI Service Interfaces (mock-first, provider-swappable)

### 7.1 LLM Provider Interface
```python
# app/ai_core/llm/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel

class LLMMessage(BaseModel):
    role: str          # "system" | "user" | "assistant"
    content: str

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: dict | None = None

class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list[LLMMessage], *, temperature: float = 0.7,
                        max_tokens: int = 1024, response_format: str | None = None) -> LLMResponse:
        ...

    @abstractmethod
    async def complete_json(self, messages: list[LLMMessage], schema: type[BaseModel]) -> BaseModel:
        """Returns a validated Pydantic object — used for structured generation
        (roadmap plans, interview questions, ATS suggestions)."""
        ...
```
- `MockLLMProvider`: returns deterministic, template-based responses (seeded by input hash) so tests and demos are reproducible without API cost.
- `OpenAIProvider` / `GeminiProvider`: real implementations behind the same interface, selected via `settings.LLM_PROVIDER` env var (`mock | openai | gemini`). Swapping providers requires **zero changes** to service-layer code — only `core/config.py` and DI wiring change.

### 7.2 Embedding Provider Interface
```python
class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...
    @property
    @abstractmethod
    def dimension(self) -> int: ...
```
Default implementation: `SentenceTransformerProvider` (`all-MiniLM-L6-v2`, 384-dim, runs locally — no API dependency, so job matching and resume-role similarity work fully offline from day one).

### 7.3 Resume Parser Interface
Pipeline: `extractor.py` (pdfplumber for PDF, python-docx for DOCX → raw text) → `ner_pipeline.py` (regex + spaCy `en_core_web_sm` NER + a curated skills gazetteer matched against `skills_master`) → structured `ParsedResume` Pydantic model → persisted to `resume_skills/education/projects/certifications`. Designed so a future LLM-based extraction (`ai_core.llm.complete_json(ParsedResume)`) can be swapped in behind the same `ResumeParser.parse(text) -> ParsedResume` method signature.

### 7.4 Interview Feedback Generator
Uses `LLMProvider.complete_json()` with a structured `InterviewFeedback` schema (`clarity`, `correctness`, `confidence`, `tips: list[str]`). Mock provider generates rule-based feedback from answer length/keyword overlap with an ideal-answer bank, so the UI/UX and scoring pipeline are fully exercised pre-integration.

### 7.5 Vector Store (FAISS)
`ai_core/vector_store/faiss_store.py` wraps a `faiss.IndexFlatIP` (cosine via normalized inner product), one index per entity type (`resumes`, `jobs`). Index persisted to disk (`ml_core/artifacts/faiss_*.index`) and rebuilt via a scheduled/admin-triggered job. `resumes.embedding_id` / `jobs.embedding_id` store the FAISS row id for lookup.

---

## 8. ML Pipeline Architecture (Placement Prediction)

### 8.1 Feature Set
| Feature | Source | Type |
|---|---|---|
| cgpa | student_profiles | float |
| internships | student_profiles | int |
| projects_count | resume_projects (count) | int |
| certifications_count | resume_certifications (count) | int |
| skills_count | resume_skills (count) | int |
| coding_score | avg(coding_attempts.score) | float |
| aptitude_score | latest aptitude_attempts.overall_score | float |
| ats_score | latest ats_reports.overall_score | float (engineered addition) |
| interview_score | avg(interview_sessions.score) | float (engineered addition) |

### 8.2 Training Pipeline (`ml_core/placement_model/train.py`)
1. **Data ingestion** — pulls historical labeled data (`placed: bool`) from `scripts/seed_data.py`-generated synthetic dataset (`ml/datasets/placement_training.csv`) for bootstrapping; swaps to real cohort outcomes once available.
2. **Preprocessing** — missing-value imputation (median), feature scaling (StandardScaler for LR baseline; tree models use raw features).
3. **Model candidates** — trained and compared: `RandomForestClassifier`, `XGBClassifier`, `CatBoostClassifier`.
4. **Evaluation** — stratified 5-fold CV, metrics: ROC-AUC, F1, precision/recall (placement prediction is imbalance-prone → prioritize recall on "at risk" class).
5. **Model selection** — best CV ROC-AUC promoted; artifact saved as `ml_core/artifacts/placement_model_v{n}.pkl` (or `.cbm` for CatBoost) + `metadata.json` (feature list, metrics, training date, git commit).
6. **Registry** — `registry.py` reads `metadata.json` files, exposes `get_active_model()` → loaded once at app startup, cached in memory. Version stored on every `placement_predictions.model_version`.

### 8.3 Inference Path (`predict.py`)
`PlacementService.predict(user_id)` → `FeatureBuilder.build(user_id)` (queries repositories above) → `registry.get_active_model().predict_proba(features)` → persists `placement_predictions` row → returns `{probability, label, model_version, feature_snapshot}`.

### 8.4 Retraining Strategy
`scripts/train_models.py` is a standalone CLI (`python scripts/train_models.py --model xgboost`) runnable manually or via a scheduled Render Cron Job; not triggered inline on requests. Keeps inference latency low and training reproducible/offline.

---

## 9. Non-Functional Architecture

| Concern | Design |
|---|---|
| **Caching** | Read-heavy, slow-changing endpoints (`/skills/roles`, `/analytics/*`, `/jobs` list) cached via `core/cache.py` — in-memory `cachetools.TTLCache` by default, swappable for Redis (`REDIS_URL` env) with identical interface. |
| **Rate limiting** | `slowapi` middleware, per-user (by JWT sub) limits: general `100/min`, AI-heavy endpoints (`/interview/*`, `/coding/generate`, `/roadmap/generate`) `10/min`. |
| **Logging** | `structlog` → JSON logs with `request_id`, `user_id`, `route`, `latency_ms`; shipped to stdout (Render captures automatically). |
| **Error handling** | Central exception handler maps domain exceptions (`ResumeParseError`, `ModelNotFoundError`, etc.) to the standard error envelope + correct HTTP status; unhandled exceptions logged with stack trace, generic message returned to client. |
| **API docs** | FastAPI auto Swagger (`/docs`) + ReDoc (`/redoc`); `docs/API.md` curated summary kept in sync manually per module PR. |
| **Dark mode** | Tailwind `class` strategy + ShadCN theme tokens; persisted via `localStorage` + `ThemeProvider` context. |
| **Responsiveness** | Tailwind breakpoints throughout; dashboard layouts use CSS grid with `sm/md/lg` collapse to single-column + drawer nav on mobile. |
| **RBAC** | See §5.3 — enforced via FastAPI dependency, not just UI hiding. |

---

## 10. Deployment Architecture

```
GitHub (monorepo)
   │
   ├─ push to backend/**  ──► Render (Web Service)
   │                          - Docker build from backend/Dockerfile
   │                          - env vars: DATABASE_URL, SUPABASE_URL, SUPABASE_JWT_SECRET,
   │                            LLM_PROVIDER=mock, REDIS_URL(optional)
   │                          - health check: GET /health
   │                          - Render Cron Job (optional): weekly model retraining
   │
   ├─ push to frontend/** ──► Vercel
   │                          - Build: vite build
   │                          - env vars: VITE_API_BASE_URL, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY
   │
   └─ Supabase (managed)
         - PostgreSQL (schema via Alembic migration run as a Render deploy hook / manual `alembic upgrade head`)
         - Supabase Auth (email/password + Google OAuth provider configured in dashboard)
         - Supabase Storage bucket: "resumes" (private, signed-URL access)
```

### 10.1 Environments
`local` (docker-compose: FastAPI + Postgres + Redis) → `staging` (Render preview env, Vercel preview deploys per PR) → `production`.

### 10.2 CI/CD (GitHub Actions, to be added when code exists)
- `backend-ci.yml`: lint (ruff) → type-check (mypy, optional) → pytest → build Docker image.
- `frontend-ci.yml`: lint (eslint) → type-check (tsc) → build → (optional) Playwright smoke test.
- Both gate merges to `main`; Render/Vercel auto-deploy on `main` push.

---

## 11. Integration Strategy — Module Wiring Summary

| Module | Frontend Route | Backend Router | Key Tables | AI/ML Used |
|---|---|---|---|---|
| 1. Auth | `/login`, `/signup` | `auth` (verify only), `users` | users, student_profiles | — |
| 2. Resume Upload | `/resume/upload` | `resumes` | resumes + 4 child tables | Resume Parser |
| 3. ATS Analyzer | `/resume/ats` | `ats` | ats_reports | LLM (suggestions), rule engine |
| 4. Skill Gap | `/skills/gap` | `skills` | skill_gap_reports, role_skills | Embeddings (skill normalization) |
| 5. Roadmap | `/roadmap` | `roadmap` | roadmaps | LLM (plan generation) |
| 6. Readiness | `/dashboard` (widget) | `readiness` | readiness_scores | Aggregation only |
| 7. Placement Prediction | `/placement` | `placement` | placement_predictions | ML Core (XGBoost/CatBoost/RF) |
| 8. Job Matching | `/jobs/matches` | `matching` | job_matches | Embeddings + FAISS |
| 9. Interview Simulator | `/interview` | `interview` | interview_sessions/turns | LLM |
| 10. Coding Assessment | `/assessments/coding` | `coding` | coding_problems/attempts | LLM (gen) + sandboxed exec |
| 11. Aptitude | `/assessments/aptitude` | `aptitude` | aptitude_questions/attempts | Static bank (seeded) |
| 12. Job Recommendation | `/jobs` | `jobs` | jobs, companies | Embeddings (via matching) |
| 13. Student Dashboard | `/dashboard` | `dashboard` | reads modules 3,4,6,7,9 | — |
| 14. Admin Dashboard | `/admin` | `admin` | reads all, scoped by dept | — |
| 15. Analytics | `/analytics` | `analytics` | jobs, placement_predictions, skill_gap_reports | Aggregation queries |

---

## 12. Build Roadmap (for module-by-module generation)

1. **Foundation** — repo scaffold, `core/*`, DB models + Alembic migration, auth middleware, health check, Docker/docker-compose.
2. **Module 1–2** — Auth wiring + Resume Upload/Parsing (establishes the parser + storage pattern reused everywhere).
3. **Module 3–5** — ATS Analyzer, Skill Gap, Roadmap (establishes the AI Core LLM interface + mock provider).
4. **Module 6–7** — Readiness Scoring + Placement Prediction (establishes ML Core + training pipeline + sample dataset).
5. **Module 8, 12** — Job Matching + Recommendation (establishes embeddings + FAISS).
6. **Module 9–11** — Interview Simulator, Coding Assessment, Aptitude Assessment.
7. **Module 13–15** — Student/Admin/Analytics dashboards (frontend-heavy, Recharts).
8. **Hardening** — rate limiting, caching, logging polish, tests, CI, deployment configs, README, sample datasets.

This order is chosen so every later module reuses an interface established earlier (parser → AI Core → ML Core → vector store) rather than inventing new patterns per module.

---

*End of blueprint. Next step: confirm this document, then begin Phase 1 (Foundation) code generation.*
