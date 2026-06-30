# Deployment

> **OpenOwls SDD** — Read by engineers and DevOps-minded team members.
> Defines how the application is built, configured, and deployed across environments.
> Claude Code uses this file to understand deployment targets and avoid environment-specific mistakes.

> **Reconciled for HOOT:** This template assumed a React + FastAPI + Postgres app with JWT auth. HOOT's MVP is a **Streamlit app over a local ChromaDB index with no database and no auth**. The tables below reflect HOOT's actual two-stage stack (Streamlit MVP → React + FastAPI target) and its real env vars (`LLM_*`, embeddings, Chroma). `DATABASE_URL` and `JWT_SECRET` are **not used** by HOOT — don't add them.

---

## Environments

| Environment | Purpose | URL |
|-------------|---------|-----|
| Local (MVP) | Develop/test the Streamlit app on your machine | `http://localhost:8501` (Streamlit default) |
| Local (target frontend) | Develop the React app (Phase 4) | `http://localhost:5173` (Vite default) |
| Staging | Pre-production testing, shared with the team | MVP: a second Streamlit Community Cloud app · Target: `https://hoot-staging.vercel.app` |
| Production | Live application for the Temple community | MVP: Streamlit Community Cloud app · Target: `https://hoot.vercel.app` |

---

## Hosting Platforms

### MVP (Phase 1–2)
| Component | Platform | Tier | Notes |
|-----------|----------|------|-------|
| Streamlit app (UI + in-process RAG core) | Streamlit Community Cloud | Free | Auto-deploys from `main`. Secrets set in the app's **Settings → Secrets**. |
| Vector index (ChromaDB) | Local persistent dir, built at deploy/ingest time | Free | Rebuilt by running ingestion; lives at `CHROMA_PATH`. |
| Embedding model | `BAAI/bge-small-en`, downloaded at runtime | Free | Cached after first download. |
| LLM | OpenAI-compatible provider (configured via env) | Pay-per-use / free if local | `gpt-4o-mini` by default; can point at a local model. |

### Target (Phase 4)
| Component | Platform | Tier | Notes |
|-----------|----------|------|-------|
| Frontend (React 18 + Vite) | Vercel | Free | Auto-deploys from `main`. |
| Backend (FastAPI + RAG core) | Render | Free | Spins down after ~15 min inactivity (cold starts). |
| Vector store | ChromaDB on a Render persistent disk → Qdrant if scale demands | Free → paid only if needed | Persist the index so it survives restarts. |

---

## Environment Variables
<!-- Never put actual values here. Use .env.example for dummy values. -->

### RAG core / backend (used by Streamlit MVP and FastAPI target)
| Variable | Required | Description |
|----------|----------|-------------|
| `LLM_BASE_URL` | Yes | Base URL of the OpenAI-compatible LLM endpoint |
| `LLM_API_KEY` | Yes | API key for the LLM provider (server-side only) |
| `LLM_MODEL` | Yes | Model name (default `gpt-4o-mini`) |
| `EMBEDDING_MODEL` | No | Embedding model (default `BAAI/bge-small-en`) |
| `CHROMA_PATH` | No | Path to the persistent ChromaDB index (default `./chroma`) |
| `ENVIRONMENT` | Yes | `local`, `staging`, or `production` |

### Frontend (Phase 4 only)
| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | Yes | Base URL of the FastAPI backend |

> ⚠️ Never commit `.env` files. Add them to `.gitignore`. Keep a `.env.example` with dummy values checked in.
> **Not used by HOOT:** `DATABASE_URL` (no relational DB in the MVP), `JWT_SECRET` (no auth). Don't add them "just in case."

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- (Phase 4 only) Node.js 20+ for the React frontend
- An API key for an OpenAI-compatible LLM provider — **or** a local model (Ollama / vLLM) exposing an OpenAI-compatible endpoint
- Enough disk for the embedding model and Chroma index

### Steps — MVP (Streamlit)

```bash
# 1. Clone the repository
git clone [repo-url]
cd hoot

# 2. Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env             # Fill in LLM_BASE_URL, LLM_API_KEY, LLM_MODEL

# 4. Add documents and build the index
#    Place public Temple documents in data/ , then:
python src/ingest.py

# 5. Run the app
streamlit run src/app.py         # serves on http://localhost:8501
```

### Steps — Target frontend (Phase 4)

```bash
# In a new terminal, with the FastAPI backend running:
cd frontend
cp .env.example .env             # set VITE_API_BASE_URL to the backend URL
npm install
npm run dev                      # serves on http://localhost:5173
```

---

## Deployment Process

### MVP — Streamlit Community Cloud
1. Push to `main` — the connected Streamlit app auto-deploys.
2. Set `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` (and any others) in the app's **Settings → Secrets** (never in the repo).
3. Ensure the index exists: either commit a prebuilt `chroma/` (if small and public) or run ingestion as part of startup. Confirm the corpus is public-only.
4. Verify the live app answers a known question with correct citations and defers correctly on an out-of-corpus question.

### Target — Frontend (Vercel)
1. Push to `main` — Vercel auto-deploys.
2. Set `VITE_API_BASE_URL` in the Vercel dashboard (**Settings → Environment Variables**).
3. Check status at `https://vercel.com/dashboard`.

### Target — Backend (Render)
1. Push to `main` — Render auto-deploys.
2. Set `LLM_*`, `EMBEDDING_MODEL`, `CHROMA_PATH`, `ENVIRONMENT` in the Render dashboard (**Environment**).
3. First deploy may take 3–5 minutes; expect cold starts after inactivity on the free tier.
4. Attach a persistent disk for the Chroma index so it survives restarts.
5. Check logs at `https://dashboard.render.com`.

---

## CI/CD Pipeline

GitHub Actions runs on every pull request:
- Linting: `black --check` (Python); `eslint` (frontend, Phase 4)
- Unit tests: `pytest` (backend/RAG core); `jest`/`vitest` (frontend, Phase 4)
- Build check (frontend, Phase 4)

Merging to `main` triggers automatic deployment to staging (Streamlit app / Vercel + Render).
Production promotion is manual and requires sponsor/faculty approval.

---

## Common Deployment Issues

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| App errors on first question | Missing `LLM_API_KEY` / `LLM_BASE_URL` | Set them in Streamlit Secrets / Render env; redeploy. |
| Every question defers | Index empty or not found | Run `python src/ingest.py`; confirm `CHROMA_PATH` matches where the index was built. |
| Answers cite nothing / poor matches | Embedding model mismatch between ingest and query | Use the same `EMBEDDING_MODEL` for both; re-ingest if changed. |
| Slow first response after idle | Render free-tier cold start | Expected; add a health-check ping or upgrade tier if needed. |
| Frontend can't reach backend (Phase 4) | Wrong `VITE_API_BASE_URL` | Confirm the backend URL in Vercel env vars. |
| LLM cost/quota spikes | No rate limiting / abuse | Add rate limiting (see `auth-security.md`); check provider dashboard. |

---

## Secrets Management

- All secrets live in the hosting platform's environment/secret settings, never in code.
- Rotate `LLM_API_KEY` immediately if it is ever committed or exposed.
- Each environment (local, staging, production) uses its own separate keys.
- Students use their **own personal API keys** for local development.
- The LLM key is only ever set where server-side code runs (Streamlit host / Render) — never exposed to the React frontend or browser.
