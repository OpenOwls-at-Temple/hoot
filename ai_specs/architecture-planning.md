# Architecture Planning

> **OpenOwls SDD** — Read by the system architect and software engineers.
> Defines the folder structure, key design decisions, and implementation details.
> Claude Code uses this file to understand how the codebase is organized.

---

## System Architecture Overview

HOOT is a **Retrieval-Augmented Generation (RAG)** system built in two stages around a single, framework-agnostic Python core.

- **MVP (Phase 1–2):** A Streamlit app calls the RAG core in-process. There is no separate API server and no relational database — the only persistent store is a local ChromaDB index built by the ingestion pipeline.
- **Target (Phase 4):** A React frontend calls a FastAPI backend over a REST API. The FastAPI service wraps the **same** RAG core. Moving from Streamlit to React + FastAPI is a frontend/transport swap, not a rewrite, because no RAG logic lives inside Streamlit.

The defining constraint: **the LLM never answers from its own knowledge.** Retrieval assembles a small set of verified Temple document chunks, and the LLM is instructed to answer only from those chunks or to defer. Full LLM behavior, prompts, and guardrails live in `llm-integration.md`.

```
                 ┌─────────────────────────┐
   MVP:          │   Streamlit UI (app.py) │
                 └────────────┬────────────┘
                              │ (in-process call)
   Target:  React UI ──HTTP──▶│ FastAPI route (/api/ask)
                              ▼
                 ┌─────────────────────────┐
                 │   RAG core (framework-   │   rag/service.py
                 │   agnostic Python)       │   llm/client.py, llm/prompts.py
                 └────────────┬────────────┘
                              ▼
         embed → hybrid retrieve (Chroma + BM25) → rerank (FlashRank)
                              ▼
                 build prompt → LLMClient.chat() (OpenAI-compatible)
                              ▼
                 parse + validate JSON → {answered, answer, citations}

   Offline:  ingest.py  →  data/ documents → chunk → embed → ChromaDB (with metadata)
```

---

## Folder Structure
<!-- Intended structure. The RAG core is framework-agnostic so it serves both Streamlit and FastAPI. -->

```
project-root/
├── CLAUDE.md
├── progress.md
├── requirements.txt
├── .env.example
├── .gitignore
├── ai_specs/                  # The SDD spec files (this folder)
├── data/                      # Source documents to ingest (git-ignored if large)
├── chroma/                    # Persistent ChromaDB index (git-ignored)
│
├── src/                       # MVP code (current state)
│   ├── ingest.py              # Ingestion pipeline (offline): load → chunk → embed → store
│   └── app.py                 # Streamlit UI (MVP) — thin; delegates to the RAG core
│
├── llm/                       # Framework-agnostic LLM layer (no Streamlit/FastAPI imports)
│   ├── client.py              # LLMClient: OpenAI-compatible wrapper (reads LLM_* env vars)
│   └── prompts.py             # All prompt templates — never inlined elsewhere
│
├── rag/                       # Framework-agnostic RAG layer (no UI imports)
│   ├── retriever.py           # Hybrid retrieval: Chroma + BM25 ensemble + FlashRank rerank
│   └── service.py             # Orchestrates: embed → retrieve → prompt → LLM → parse/validate
│
├── tests/                     # Mirrors source layout (test_service.py, test_client.py, ...)
│
└── backend/                   # Target architecture (Phase 4) — added later
    └── app/
        ├── main.py            # FastAPI app
        ├── routes/            # API route handlers (ask.py, health.py, feedback.py)
        ├── schemas/           # Pydantic request/response schemas
        └── (imports llm/ and rag/ unchanged)
   # frontend/  (React 18 + Vite) is added alongside in Phase 4
```

> **Current vs. intended:** `progress.md` shows the MVP was first built as two files (`src/ingest.py`, `src/app.py`) with retrieval logic inline in `app.py`. The intended end state factors the answer pipeline into `rag/` and `llm/` so it has **zero** Streamlit imports. Refactoring `app.py` to call `rag/service.py` is the bridge that makes the FastAPI migration a swap rather than a rewrite — do this before Phase 4.

---

## Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| App pattern | RAG (retrieve-then-generate) | The whole point is grounded, sourced answers — retrieval must constrain generation. |
| RAG framework | **LangChain** | Matches the working implementation (`EnsembleRetriever`, `ContextualCompressionRetriever`, `ChatOpenAI`). ⚠️ Original spec said LlamaIndex — see `overview.md` conflict note. |
| Retrieval strategy | Hybrid: dense (Chroma) + sparse (BM25) ensemble, then FlashRank rerank | Dense catches semantic matches, BM25 catches exact terms (policy names, acronyms like FMLA); reranking lifts the best chunk into top-k. |
| Vector store | ChromaDB (local, persistent) | Zero-infra, free, fine for hundreds–thousands of chunks. Graduate to Qdrant / pgvector only if scale demands. |
| Embeddings | `BAAI/bge-small-en` (local) | Free, runs locally, strong for retrieval; keeps MVP cost at $0. Must use the **same** model at ingestion and query time. |
| Chunking | By section/heading, not fixed character count | Keeps a policy section semantically whole so citations point to a coherent passage. |
| LLM access | OpenAI-compatible wrapper, server-side only | Vendor-neutral, swappable by config; key never reaches the client. See `llm-integration.md`. |
| Output contract | Structured JSON (`answered`, `answer`, `citations`) | Lets the UI reliably distinguish a real answer from a deferral and render citations. |
| Default posture | Defer when uncertain | A wrong HR answer is worse than no answer; empty retrieval / bad JSON / low confidence all resolve to "contact HR." |
| Auth (MVP) | None | Corpus is public, app is read-only, no PII stored — nothing to protect with login. See `auth-security.md`. |
| Core isolation | RAG core has no UI/framework imports | Enables the Streamlit → FastAPI migration without rewriting the pipeline. |

---

## Data Models
<!-- HOOT has no user/relational database. Its "data models" are the document chunk and the answer contract. -->

> **Note:** Unlike a typical CRUD app, HOOT stores **no users, no tasks, no records**. The only persisted data is the vector index of public document chunks. The two core structures are below.

### Document Chunk (stored in ChromaDB)
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Stable chunk identifier (e.g., source + section hash) |
| `text` | string | The chunk's text content |
| `embedding` | float[] | Vector from `BAAI/bge-small-en` (managed by Chroma) |
| `title` | string (metadata) | Human-readable document/section title |
| `url` | string (metadata) | Link to the original public source |
| `category` | enum (metadata) | `benefits` \| `policy` \| `research` \| `conduct` |
| `last_updated` | date (metadata) | When the source document was last updated |
| `source` | string (metadata) | Origin file/URL the chunk was ingested from |

### Answer Contract (returned by `rag/service.py`)
| Field | Type | Description |
|-------|------|-------------|
| `answered` | boolean | `true` if grounded in retrieved context; `false` triggers the deferral UI |
| `answer` | string | Plain-language answer, or the standard "contact HR" deferral message |
| `citations` | array | Only the sources actually used: `{ title, url, category, last_updated }` |

---

## API Endpoints
<!-- MVP has none (Streamlit calls the core in-process). These are the Phase 4 / FastAPI target endpoints. -->

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/ask` | Body `{ question, history? }` → `{ answered, answer, citations }`. The core RAG endpoint. |
| GET | `/api/health` | Liveness/readiness check (used by Render and uptime checks). |
| POST | `/api/feedback` | *(Phase 2/3)* Body `{ question, sources, rating }` → records thumbs up/down. No PII. |

> **MVP:** the Streamlit app imports `rag.service` and calls it directly; there is no HTTP surface. The endpoints above describe the target architecture only.

---

## LLM Integration
<!-- Where the LLM layer plugs into the architecture. Full details live in llm-integration.md. -->

- **Where the LLM layer lives:** `llm/` (client + prompts) and `rag/service.py` (orchestration). Called **server-side only** — from the Streamlit process in the MVP, from FastAPI in the target.
- **Prompts:** centralized in `llm/prompts.py`; never inlined in UI or route code (see `conventions.md`).
- **Full details:** model choice, prompt text, context/token strategy, error handling, privacy, and evaluation are all in `ai_specs/llm-integration.md`.

---

## Environment Variables
<!-- Never put actual values here. See deployment.md and .env.example. -->

| Variable | Description |
|----------|-------------|
| `LLM_BASE_URL` | Base URL of the OpenAI-compatible LLM endpoint |
| `LLM_API_KEY` | API key for the LLM provider (server-side only) |
| `LLM_MODEL` | Model name (MVP default: `gpt-4o-mini`) |
| `EMBEDDING_MODEL` | Embedding model name (default: `BAAI/bge-small-en`) |
| `CHROMA_PATH` | Filesystem path to the persistent ChromaDB index |
| `ENVIRONMENT` | `local`, `staging`, or `production` |
| `VITE_API_BASE_URL` | *(Phase 4, frontend)* Base URL of the FastAPI backend |

> ⚠️ Note: HOOT does **not** use `DATABASE_URL` or `JWT_SECRET` in the MVP — there is no relational DB and no auth. Don't add them "just in case."

---

## Deployment
<!-- Deployment details are covered in ai_specs/deployment.md -->

See `ai_specs/deployment.md` for environments, hosting platforms, and the deploy process for both the Streamlit MVP and the React + FastAPI target.
