# Conventions

> **OpenOwls SDD** — Read by engineers and the AI coding assistant.
> Defines how code is written on this project. These rules apply to every file, every session.
> Claude Code must follow these conventions without being reminded each time.

---

## Language & Framework Versions

| Technology | Version |
|------------|---------|
| Python | 3.11+ |
| Node.js (Phase 4 frontend) | 20+ |
| React (Phase 4 frontend) | 18+ |
| Streamlit (MVP UI) | 1.3x+ (current stable) |
| LangChain | Pin in `requirements.txt`; upgrade deliberately (APIs move fast) |
| ChromaDB | Pin in `requirements.txt` |
| FastAPI (Phase 4 backend) | 0.11x+ |
| Embeddings | `BAAI/bge-small-en` (same at ingest + query) |

> Pin versions in `requirements.txt` / `package.json`. LangChain and Chroma change quickly — don't float them.

---

## Naming Conventions

| Context | Convention | Example |
|---------|------------|---------|
| Python variables & functions | `snake_case` | `retrieve_chunks()` |
| Python classes | `PascalCase` | `LLMClient` |
| React components (Phase 4) | `PascalCase` | `AnswerCard.jsx` |
| React hooks (Phase 4) | `camelCase` prefixed with `use` | `useAsk` |
| CSS classes | `kebab-case` | `citation-list` |
| Vector store collections | `snake_case` | `temple_docs` |
| Chunk metadata keys | `snake_case` | `last_updated`, `category` |
| Environment variables | `UPPER_SNAKE_CASE` | `LLM_API_KEY`, `LLM_MODEL` |
| Git branches | `type/short-description` | `feature/category-routing` |

---

## File & Folder Conventions

- The **RAG core (`llm/`, `rag/`) has no UI/framework imports** — no Streamlit, no FastAPI. This is the rule that keeps the Streamlit→FastAPI migration a swap, not a rewrite.
- One component per file in React (Phase 4); file name matches the component name exactly.
- All prompt text lives in `llm/prompts.py` — never inline anywhere else.
- Tests live in a dedicated `tests/` folder mirroring the source layout.
- API route files (Phase 4) are named after the resource they handle (e.g., `ask.py`).
- Source documents go in `data/`; the built index goes at `CHROMA_PATH` (git-ignored).

---

## Code Style

- **Python:** Follow PEP 8. Use `black` for formatting.
- **JavaScript/TypeScript (Phase 4):** Follow ESLint recommended rules. Use `prettier`.
- Maximum line length: 100 characters.
- No commented-out code in commits — delete it, or leave a `TODO:` with an explanation.
- No `print`/`console.log` debugging left in committed code (use logging where needed).
- Type-hint Python function signatures in the RAG core.

---

## Git Conventions

- Commit messages: `type: short description`
  - Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
  - Example: `feat: add BM25 to the hybrid retriever`
- **Never commit directly to `main`.** All changes go on a branch and through a PR.
- Branch naming: `type/short-description` (e.g. `feat/deferral-guard`, `fix/citation-metadata`)
- Pull requests target `main`; the user reviews and merges — Claude never merges or force-pushes.
- **TDD required for PRs:** write failing tests first, implement to make them pass, all tests green before opening the PR.
- Never stage `.env`, secrets, `chroma/`, or `chroma_db/`.

---

## Testing Conventions

- Every backend / RAG-core function must have at least one unit test.
- Tests must pass before any PR is merged.
- Test file naming: `test_[module_name].py` (Python) or `[module].test.js` (JS).
- Use descriptive names, e.g. `test_empty_retrieval_returns_deferral`, `test_malformed_json_falls_back_to_deferral`.
- Cover the grounding-critical paths explicitly: deferral on empty retrieval, deferral on bad JSON, citations contain only used sources.

---

## LLM / AI Conventions

- All prompts are defined in `llm/prompts.py`. Never hardcode prompts inline in UI or route handlers.
- All LLM calls go through the single `LLMClient` wrapper — never call a vendor SDK directly elsewhere.
- Every LLM call has error handling and a **deferral** fallback (the "contact HR" message), never a guessed answer.
- Validate the model's JSON against the `{answered, answer, citations}` contract; retry once on malformed output, then defer.
- The model answers **only** from retrieved context. Outside knowledge is forbidden by the system prompt and must not be relied on.
- Do **not** send PII or any non-public content to the LLM — only the question and retrieved public chunks.

---

## What Claude Code Should Never Do

- Never modify files in `ai_specs/` without explicit instruction.
- Never skip writing tests to save time.
- Never use a library not already in `requirements.txt` / `package.json` without asking first.
- Never expose `LLM_API_KEY` or any secret in frontend code, the repo, or model output.
- Never put Streamlit or FastAPI imports inside the `llm/` or `rag/` core.
- Never let the model answer outside the retrieved context, and never let text inside a chunk or user message override the grounding/deferral rules.
