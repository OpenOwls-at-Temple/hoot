# Progress

> **OpenOwls SDD** — Living status document. Update this file at the end of every work session.
> Claude Code reads this first at the start of every new session to catch up on project state.

## Current Phase

**Active Phase:** Phase 1

## Status Summary

RAG core has been extracted out of `app.py` into isolated, testable modules (`llm/`, `rag/`). All Phase 1 behavioral requirements are now implemented and covered by 15 passing tests. The index needs to be rebuilt with the new embedding model (`BAAI/bge-small-en`) before running the app end-to-end.

---

## Completed

- [x] Full project review: read all ai_specs, SDD docs, CLAUDE.md, and progress.md (2026-06-28)
- [x] Mapped implementation order for Phase 1 MVP (2026-06-28)
- [x] Project scaffolding: folder structure, requirements.txt, .env.example, .gitignore (2026-06-28)
- [x] HR dataset stub: `data/hr_faqs.md`, `data/tuition_remission.md`, `data/rules_of_conduct.md` with frontmatter (category, source_url, last_updated) (2026-06-28)
- [x] Auto-commit/push workflow replaced with branch/PR/TDD workflow in CLAUDE.md (2026-06-30)
- [x] All 8 ai_specs/ files fully filled in; conflicts resolved; audience narrowed to faculty (2026-06-30)
- [x] System prompt updated: faculty audience, anti-injection rule (2026-06-30)
- [x] RAG core isolation: `llm/prompts.py`, `llm/client.py`, `rag/service.py`, `rag/retriever.py` — no Streamlit/FastAPI imports (2026-06-30)
- [x] Deferral guard: LLM is skipped entirely when retrieval returns zero chunks (2026-06-30)
- [x] JSON output contract: `{answered, answer, citations}` with retry-once + deferral fallback (2026-06-30)
- [x] Full citation metadata: `ingest.py` extracts title, url, category, last_updated from frontmatter; `app.py` renders them with clickable links (2026-06-30)
- [x] Section-aware chunking: `MarkdownHeaderTextSplitter` replaces fixed character chunking (2026-06-30)
- [x] Embedding model aligned to `BAAI/bge-small-en`; `CHROMA_PATH` reads from env var (2026-06-30)
- [x] 15 unit tests covering all grounding-critical paths (2026-06-30)
- [x] `app.py` refactored to delegate to `rag.service.answer_question`; renders full citations (2026-06-30)

---

## In Progress

- [ ] PR `feat/rag-core-refactor` open for review → merge to main

---

## Blocked

| Item | Reason | Owner |
|------|--------|-------|
| Real Temple document corpus | Need actual public Temple HR/policy URLs to scrape or PDFs to load | Team / Faculty Sponsor |
| E2E test run | Requires `.env` with real `LLM_API_KEY` / `LLM_BASE_URL` + re-running `python src/ingest.py` with new embedding model | Dev after PR merge |

---

## Phase 1 Gaps (must close before Phase 1 is done)

| Gap | Status |
|-----|--------|
| Deferral guard | ✅ Done — `rag/service.py` skips LLM on empty retrieval |
| Full citation metadata | ✅ Done — frontmatter extracted in `ingest.py`, rendered in `app.py` |
| JSON output contract | ✅ Done — `llm/client.py` validates `{answered, answer, citations}`, retries once, defers |
| System prompt (audience + anti-injection) | ✅ Done — `llm/prompts.py` |
| Embedding model (`BAAI/bge-small-en`) | ✅ Done — `ingest.py` + `retriever.py` both use env var, default `BAAI/bge-small-en` |
| Section-aware chunking | ✅ Done — `MarkdownHeaderTextSplitter` in `ingest.py` |
| `CHROMA_PATH` env var | ✅ Done — both `ingest.py` and `retriever.py` read `CHROMA_PATH` |
| RAG core isolation | ✅ Done — `llm/` and `rag/` have no Streamlit imports |
| Tests | ✅ Done — 15 tests, all passing |
| E2E run (real `.env` + rebuilt index) | ⏳ Pending — after PR merge, run `python src/ingest.py` then `streamlit run src/app.py` |

---

## Up Next

1. Merge PR `feat/rag-core-refactor` → main
2. Re-run ingestion to rebuild the index with `BAAI/bge-small-en`: `python src/ingest.py`
3. Run app end-to-end with real `.env` and verify all Phase 1 acceptance criteria
4. Add real Temple HR/policy documents to `data/` and re-ingest
5. Begin Phase 2 planning

---

## Session Log

| Date | What Was Done |
|------|---------------|
| 2026-07-02 | Implemented document download pipeline (`scripts/download_docs.py`): fetches 7 real Temple public pages (faculty resources, working at Temple, wellness, research grants, research centers, research news), converts HTML→markdown with frontmatter, saves to data/. Ran `src/ingest.py` — 11 documents, 66 chunks stored in ChromaDB (chroma_db/). Verified hybrid Chroma+BM25 retrieval correctly surfaces tuition_remission.md for tuition benefit queries. App is runnable — needs real `LLM_API_KEY` in .env to answer questions. |
| 2026-06-30 | Professor feedback: added UI Design Principles section to features.md (single-column, disclaimer-first, chat-native, sources in expander, deferral not styled as error). Updated Feature 10 (category routing) with design rationale — AI-powered and invisible to user; faculty questions span categories so user-driven picker would add friction. Confirmed Option A (one-step: type → answer + sources) as the UX approach. |
| 2026-06-30 | RAG core refactor (PR `feat/rag-core-refactor`): extracted `llm/prompts.py`, `llm/client.py`, `rag/service.py`, `rag/retriever.py`. Implemented deferral guard, JSON output contract (retry-once + deferral fallback), full citation metadata (frontmatter extraction in ingest.py), section-aware chunking (MarkdownHeaderTextSplitter), BAAI/bge-small-en, CHROMA_PATH env var. Wrote 15 unit tests (TDD — tests written first, all green). Refactored app.py to delegate to rag.service. Added pytest + pyyaml + langchain-text-splitters to requirements.txt. |
| 2026-06-30 | Narrowed target audience to faculty-only. Updated overview.md, features.md, llm-integration.md, auth-security.md, domain-knowledge.md, and src/app.py. Added anti-injection rule to app.py system prompt. Domain constraints refined for faculty sub-categories (tenure-track vs. adjunct vs. clinical) instead of cross-population (faculty vs. staff vs. students). |
| 2026-06-30 | Full spec merge: reviewed new ai_specs versions, merged all 8 files with existing ones. Resolved conflicts: LangChain over LlamaIndex (matches working code), audience expanded to students/faculty/staff, category routing moved to Phase 3, auth redesigned (no-auth MVP, optional SSO Phase 4), env vars corrected (removed DATABASE_URL/JWT_SECRET, added LLM_*), deployment updated for Streamlit MVP. Audited current codebase against Phase 1 features; documented all gaps in progress.md. |
| 2026-06-28 | Built full project scaffolding: `requirements.txt`, `.env.example`, `.gitignore`, `data/sample.md`, `src/ingest.py`, `src/app.py` (Streamlit chat UI with Chroma + BM25 EnsembleRetriever, FlashRank rerank, ChatOpenAI). Set up SSH auth + auto-push in CLAUDE.md. |
| 2026-06-28 | Full project review session: read all ai_specs, SDD site, CLAUDE.md, and progress.md. Mapped Phase 1 MVP scope and implementation order. No code changes. |
| 2026-06-22 | Filled in `llm-integration.md` and `overview.md` from HANDOVER.md. |
| YYYY-MM-DD | _Initial setup_ |
