# Overview

> **OpenOwls SDD** — Read by the business sponsor and the full team.
> Describes the project at a high level: what it is, why it exists, who it is for, and what technology it uses.

---

## Project Name

**HOOT — Helpful Owl Of Temple**

## One-Line Description

A citation-backed answer engine that helps the Temple University community — students, faculty, and staff — get trustworthy answers to HR, benefits, policy, and conduct questions, drawn **only** from Temple's own published documents, each linked back to its source.

---

## Problem Statement

Temple's public HR and policy information is genuinely public but fragmented across at least four separate systems. A faculty member asking *"is my graduate tuition benefit taxable?"* must dig through a benefits-summary PDF, while *"can I teach at another university?"* lives in the Faculty Handbook on a completely different subdomain. A student worker asking about pay schedules, or a staff member asking about FMLA, faces the same scavenger hunt. There is no single place to ask a plain-language question and get a reliable, sourced answer.

HOOT solves this with a Retrieval-Augmented Generation (RAG) pipeline: it retrieves the right Temple document and answers **only** from it, always with a citation back to the source. The guiding principle is that for HR content, a confidently wrong answer (e.g., about FMLA eligibility or tuition-benefit taxability) is worse than no answer. Every design decision serves two goals: **retrieve the right chunk, and don't hallucinate beyond it.**

---

## Goals

- **Accurate, sourced answers.** Every answer cites and links the Temple document it came from; no answer is given without a source.
- **No hallucination.** When the answer isn't in Temple's published documents, HOOT says so and points the user to HR rather than guessing.
- **Reduce time-to-answer.** A community member gets a sourced answer in seconds instead of searching multiple websites and PDFs.
- **Serve the whole Temple community.** Students, faculty, and staff can all ask questions; answers surface the document and note who it applies to where the source makes that clear.
- **Demoable in one semester.** Ship a working MVP (ask a question → get a cited answer) that can be shown to the community and stakeholders.
- **Measurable retrieval quality.** Build a test set of 30–50 real questions with known correct sources and measure retrieval + answer quality against it.

## Non-Goals

- **Not official HR advice, and not legal advice.** HOOT is an informational assistant; the actual Temple documents and HR staff remain authoritative.
- **No PII.** HOOT does not connect to individual employee or student records and does not collect personal data — it stays purely informational.
- **Nothing behind login.** Only publicly accessible documents are ingested; nothing behind the TUportal login is touched, and `robots.txt` is respected.
- **Not a general-purpose chatbot.** It answers from Temple's document corpus only — it is not a free-form conversational AI.

---

## Target Users

| User Type | Description |
|-----------|-------------|
| Primary Users | Temple University **students, faculty, and staff** asking natural-language questions about HR policy, benefits, research/funding opportunities, and conduct rules. |
| Secondary Users | Temple HR / Faculty Affairs staff, who validate accuracy and may provide cleaner source data. |
| Internal Users | The OpenOwls student team building, testing, and maintaining the system (also responsible for the ingestion pipeline). |

> **Audience note:** Some policies apply only to a subset of the community (e.g., tuition remission rules differ for staff vs. faculty; some benefits are employee-only). HOOT does **not** try to infer a user's role — it answers from the document and lets the cited source speak to who is covered. See `domain-knowledge.md`.

---

## Tech Stack

HOOT ships in two stages. The **MVP** proves the RAG pipeline works with the least possible ceremony (Streamlit). The **target architecture** — a React frontend on a FastAPI backend — is the committed end state the project is deliberately building toward; the MVP is a stepping stone to it, not a throwaway.

| Layer | MVP (Phase 1–2) | Target (Phase 4) | Notes |
|-------|-----------------|-------------------|-------|
| UI / Frontend | Streamlit | React 18 | Streamlit gives a working chat box fast; React is the ultimate polished, deployable frontend. |
| Backend / API | (in-process, served by Streamlit) | FastAPI (Python) | RAG logic is written as plain Python modules from day one so it lifts cleanly into a FastAPI service later. |
| RAG framework | **Python + LangChain** | **Python + LangChain** | ⚠️ See conflict note below. Implemented with LangChain (`EnsembleRetriever`, `ContextualCompressionRetriever`, FlashRank rerank, `ChatOpenAI`). |
| Vector store | ChromaDB (local, persistent) | ChromaDB → Qdrant or Postgres + pgvector | Start with zero-infra local Chroma; graduate only if scale requires it. |
| Embeddings | `BAAI/bge-small-en` (free/local) | same, or OpenAI `text-embedding-3-small` | Local embeddings keep cost at zero for the MVP. |
| Retrieval | Hybrid: Chroma (dense) + BM25 (sparse) ensemble, FlashRank rerank | same | Hybrid + rerank improves recall and precision over dense-only. |
| LLM | `gpt-4o-mini` via OpenAI-compatible wrapper | Any OpenAI-compatible provider (incl. Claude via gateway, or local Llama/Mistral) | Small + cheap is plenty — retrieval does the heavy lifting. Called server-side only. See `llm-integration.md`. |
| Evaluation | RAGAS | RAGAS | Added once a test question set exists (Phase 3). |
| Hosting | Streamlit Community Cloud (free) | Vercel (frontend) + Render (backend) | Free tiers throughout. |

> **Architecture note for the team:** Write the ingestion and query pipeline as standalone, framework-agnostic Python (no Streamlit-specific logic inside the RAG core). This is what makes the eventual move from Streamlit to FastAPI + React a frontend swap rather than a rewrite.

> **⚠️ Conflict reconciled (RAG framework):** The original stack table named **LlamaIndex**, but the code already built (`src/ingest.py`, `src/app.py`, per `progress.md`) uses **LangChain** APIs. These specs are aligned to LangChain to match the working implementation. If the team genuinely wants LlamaIndex, the existing RAG core would need to be rewritten — decide deliberately rather than letting the docs and code drift apart.

---

## Stakeholders

| Name / Role | Responsibility |
|-------------|----------------|
| Faculty Sponsor | Defines scope, reviews milestones, owns `overview.md` and `features.md`. |
| Student Team (OpenOwls) | Design, implementation, evaluation, deployment, and ingestion maintenance. |
| Temple HR / Faculty Affairs | **Recommended to loop in early** — provides accuracy validation, possibly cleaner source data, and goodwill; heads off "is this official?" confusion. |
| Community Testers | A few willing students, faculty, and staff who test answers and give feedback in later phases. |

---

## Key Constraints

- **Time:** Should reach a demoable MVP within one semester.
- **Budget:** Free-tier cloud services and free/local models only; no paid infrastructure.
- **Data scope:** Public Temple documents only — respect `robots.txt`, never touch anything behind the TUportal login.
- **Accuracy-critical:** This is HR content. The system must defer ("I couldn't find that in Temple's published documents — contact HR") rather than answer when it is uncertain.
- **Stack direction is fixed:** React + FastAPI is the committed target architecture; the Streamlit MVP must be built so it does not lock the team out of that path.
