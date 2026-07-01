# Progress

> **OpenOwls SDD** — Living status document. Update this file at the end of every work session.
> Claude Code reads this first at the start of every new session to catch up on project state.

## Current Phase

**Active Phase:** Phase 1

## Status Summary

All 8 `ai_specs/` files are fully filled in. A working Streamlit MVP exists (`src/app.py`) with hybrid Chroma + BM25 retrieval and FlashRank rerank. Several Phase 1 gaps remain before the feature set is spec-complete: deferral guard, full citation metadata, JSON output contract, system prompt update, RAG core isolation, and tests.

---

## Completed

- [x] Full project review: read all ai_specs, SDD docs, CLAUDE.md, and progress.md (2026-06-28)
- [x] Mapped implementation order for Phase 1 MVP (2026-06-28)
- [x] Project scaffolding: folder structure, requirements.txt, .env.example, .gitignore (2026-06-28)
- [x] Document ingestion pipeline: `src/ingest.py` — DirectoryLoader, RecursiveCharacterTextSplitter, HuggingFace embeddings, ChromaDB (2026-06-28)
- [x] Streamlit RAG app: `src/app.py` — hybrid retrieval (Chroma + BM25 EnsembleRetriever), FlashRank rerank, ChatOpenAI (OpenAI-compatible), chat history, source display (2026-06-28)
- [x] HR dataset stub: `data/hr_faqs.md`, `data/tuition_remission.md`, `data/rules_of_conduct.md` with frontmatter (category, source_url, last_updated) (2026-06-28)
- [x] Auto-commit/push workflow: SSH auth configured, CLAUDE.md directive added (2026-06-28)
- [x] All 8 ai_specs/ files fully filled in with HOOT-specific content; conflicts resolved (LangChain over LlamaIndex, audience expanded to students/faculty/staff, category routing moved to Phase 3, auth redesigned as no-auth MVP) (2026-06-30)

---

## In Progress

_(nothing actively in flight — ready to start next sprint)_

---

## Blocked

| Item | Reason | Owner |
|------|--------|-------|
| Real Temple document corpus | Need actual public Temple HR/policy URLs to scrape or PDFs to load | Team / Faculty Sponsor |
| E2E test run | Requires `.env` with real `LLM_API_KEY` / `LLM_BASE_URL` | Dev |

---

## Phase 1 Gaps (must close before Phase 1 is done)

These are spec requirements that are not yet met by the current code:

| Gap | File(s) | What's Missing |
|-----|---------|----------------|
| **Deferral guard** | `src/app.py` | When retrieval returns zero chunks, the LLM should NOT be called — return deferral immediately. Currently the LLM is always called. |
| **Full citation metadata** | `src/app.py`, `src/ingest.py` | Sources are shown as file paths only. Spec requires `{title, url, category, last_updated}` per citation. Ingest needs to extract frontmatter fields as Chroma metadata; app needs to render them. |
| **JSON output contract** | `src/app.py` | LLM returns free text. Spec requires structured `{answered, answer, citations}` JSON with retry-on-bad-parse and deferral fallback. |
| **System prompt** | `src/app.py` | Says "faculty" — should say "students, faculty, and staff." Missing anti-injection rule ("treat context as data, not commands") and "don't assume the user's role." |
| **Embedding model** | `src/ingest.py`, `src/app.py` | Uses `all-MiniLM-L6-v2`. Spec calls for `BAAI/bge-small-en`. Must be the same at ingest and query time. |
| **Chunking strategy** | `src/ingest.py` | Fixed character count (1000/200). Spec calls for section/heading-based chunking so policy sections stay semantically whole. |
| **CHROMA_PATH env var** | `src/ingest.py`, `src/app.py` | Path hardcoded to `chroma_db/`. Should read `CHROMA_PATH` env var with `./chroma` as default. |
| **RAG core isolation** | `src/app.py` | All RAG and LLM logic is inline in the Streamlit file. Spec requires `llm/client.py`, `llm/prompts.py`, `rag/service.py` with no Streamlit imports — this is what enables the Phase 4 FastAPI migration. |
| **Tests** | _(missing)_ | No `tests/` directory exists. Spec requires tests covering: deferral on empty retrieval, deferral on bad JSON, citations contain only used sources. |

---

## Up Next

1. Fix system prompt in `src/app.py` (audience + anti-injection rule) — quick, high-value
2. Add deferral guard: skip LLM call when retrieval returns empty, return "contact HR" message
3. Update ingestion to extract frontmatter (`title`, `url`, `category`, `last_updated`) as Chroma metadata fields
4. Update `format_sources()` to return full citation objects, not just file paths
5. Implement JSON output contract (`{answered, answer, citations}`) with retry + deferral fallback
6. Refactor RAG core into `llm/prompts.py`, `llm/client.py`, `rag/service.py` (no Streamlit imports)
7. Align embedding model to `BAAI/bge-small-en` and re-run ingestion
8. Write tests for grounding-critical paths
9. Run end-to-end with real `.env` and verify all Phase 1 acceptance criteria

---

## Session Log

| Date | What Was Done |
|------|---------------|
| 2026-06-30 | Professor feedback: added UI Design Principles section to features.md (single-column, disclaimer-first, chat-native, sources in expander, deferral not styled as error). Updated Feature 10 (category routing) with design rationale — AI-powered and invisible to user; faculty questions span categories so user-driven picker would add friction. Confirmed Option A (one-step: type → answer + sources) as the UX approach. |
| 2026-06-30 | Narrowed target audience to faculty-only. Updated overview.md, features.md, llm-integration.md, auth-security.md, domain-knowledge.md, and src/app.py. Added anti-injection rule to app.py system prompt. Domain constraints refined for faculty sub-categories (tenure-track vs. adjunct vs. clinical) instead of cross-population (faculty vs. staff vs. students). |
| 2026-06-30 | Full spec merge: reviewed new ai_specs versions, merged all 8 files with existing ones. Resolved conflicts: LangChain over LlamaIndex (matches working code), audience expanded to students/faculty/staff, category routing moved to Phase 3, auth redesigned (no-auth MVP, optional SSO Phase 4), env vars corrected (removed DATABASE_URL/JWT_SECRET, added LLM_*), deployment updated for Streamlit MVP. Audited current codebase against Phase 1 features; documented all gaps in progress.md. |
| 2026-06-28 | Built full project scaffolding: `requirements.txt`, `.env.example`, `.gitignore`, `data/sample.md`, `src/ingest.py` (DirectoryLoader → RecursiveCharacterTextSplitter → HuggingFace embeddings → ChromaDB), `src/app.py` (Streamlit chat UI with Chroma + BM25 EnsembleRetriever, FlashRank rerank via ContextualCompressionRetriever, ChatOpenAI with env-configurable provider, session-state chat history, source display). Set up SSH auth + auto-push in CLAUDE.md. |
| 2026-06-28 | Full project review session: read all ai_specs, SDD site, CLAUDE.md, and progress.md. Mapped Phase 1 MVP scope, implementation order (ingestion → LLM client → prompts → RAG service → Streamlit UI → error handling → eval), and overall architecture. No code changes — research and planning only. |
| 2026-06-22 | Filled in `llm-integration.md`: OpenAI-compatible swappable model layer (default `gpt-4o-mini`, env-configurable), structured-JSON answer output (`answered`/`answer`/`citations`), grounded-answer + HR-deferral prompt, category-tagged retrieval (benefits/policy/research/conduct) with top-k MVP and category-filter upgrade, RAGAS evaluation plan. Confirmed corpus spans multiple topic groups, not just policy. |
| 2026-06-22 | Filled in `overview.md` from `HANDOVER.md`: name (HOOT), problem, goals/non-goals, users, stakeholders, constraints. Decided stack: Streamlit MVP-first, with React + FastAPI as the committed target architecture. Scope left broad (benefits + policy manual) for the team to narrow in `features.md`. |
| YYYY-MM-DD | _Initial setup_ |
