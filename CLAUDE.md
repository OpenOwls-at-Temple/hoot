# CLAUDE.md
> This project follows the **OpenOwls SDD (Spec-Driven Development) Process**.
> Read the files below in order before doing any work.

## Session Startup — Read These First

1. **`progress.md`** (project root) — catch up on what has been done, what is in progress, and what is blocked
2. **`ai_specs/overview.md`** — understand the project goals, stakeholders, and tech stack
3. **`ai_specs/features.md`** — understand the full feature scope and which phase we are currently in
4. **`ai_specs/architecture-planning.md`** — understand folder structure, design decisions, and implementation details
5. **`ai_specs/domain-knowledge.md`** — understand domain-specific concepts and constraints
6. **`ai_specs/llm-integration.md`** — understand the LLM's role, model choice, prompt design, context strategy, and guardrails
7. **`ai_specs/conventions.md`** — follow all coding conventions, naming rules, and workflow standards without exception
8. **`ai_specs/auth-security.md`** — understand the user model, identity strategy, authentication, authorization, data protection, and threats
9. **`ai_specs/deployment.md`** — understand hosting platforms, environment variables, and deployment process

## General Instructions

- Always work within the current phase defined in `ai_specs/features.md`. Do not implement features from a future phase unless explicitly instructed.
- After completing any meaningful unit of work, update `progress.md` to reflect what was done.
- If you encounter a conflict between these spec files, flag it to the user before proceeding.
- If a spec file is missing a detail you need, ask the user rather than assuming.
- Never delete or overwrite any file in `ai_specs/` without explicit instruction.

## Branch, Commit & PR Workflow

**Never commit directly to `main`.** All work goes through a branch and a pull request that the user reviews and merges.

### For every meaningful unit of work (feature, fix, spec update, refactor, etc.):

1. **Create a branch** from the latest `main` using the conventional name format:
   - `feat/short-description` — new feature
   - `fix/short-description` — bug fix
   - `docs/short-description` — spec or documentation update
   - `refactor/short-description` — code restructuring
   - `test/short-description` — adding or updating tests
   - `chore/short-description` — tooling, config, deps

2. **Follow TDD** — write tests before (or alongside) implementation:
   - Write failing tests that define the expected behavior first.
   - Implement the code to make those tests pass.
   - All tests must pass before opening the PR.

3. **Stage and commit** only relevant files — never `.env`, secrets, `chroma/`, or `chroma_db/`.
   - Use conventional commit messages: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

4. **Push the branch** to `origin` and **open a pull request** targeting `main`:
   - PR title: concise, matches the branch type (e.g. `feat: add deferral guard to RAG service`)
   - PR body: what changed, why, and a short test plan checklist
   - Assign the PR to the user for review

5. **Do not merge** — the user reviews and merges the PR. Never push directly to `main` or use `--force`.

Do all of this automatically — never wait for the user to ask.
