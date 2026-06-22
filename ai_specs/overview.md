# Overview

> **OpenOwls SDD** — Read by the business sponsor and the full team.
> Describes the project at a high level: what it is, why it exists, who it is for, and what technology it uses.

---

## Project Name

**HOOT — Helpful Owl Of Temple**

## One-Line Description

A citation-backed answer engine that helps Temple University faculty get trustworthy answers to HR, benefits, policy, and conduct questions — drawn only from Temple's own published documents, each linked to its source.

---

## Problem Statement

Temple's faculty-facing HR information is genuinely public but fragmented across at least four separate systems. A faculty member asking *"is my graduate tuition benefit taxable?"* must dig through a benefits-summary PDF, while *"can I teach at another university?"* lives in the Faculty Handbook PDF on a completely different subdomain. There is no single place to ask a plain-language question and get a reliable, sourced answer.

HOOT solves this with a Retrieval-Augmented Generation (RAG) pipeline: it retrieves the right Temple document and answers **only** from it, always with a citation back to the source. The guiding principle is that for HR content, a confidently wrong answer (e.g., about FMLA eligibility or tuition-benefit taxability) is worse than no answer. Every design decision serves two goals: retrieve the right chunk, and don't hallucinate beyond it.

---

## Goals

- **Accurate, sourced answers.** Every answer cites and links the Temple document it came from; no answer is given without a source.
- **No hallucination.** When the answer isn't in Temple's published documents, HOOT says so and points the user to HR rather than guessing.
- **Reduce time-to-answer.** A faculty member gets a sourced answer in seconds instead of searching four separate websites and PDFs.
- **Demoable in one semester.** Ship a working MVP (ask a question → get a cited answer) that can be shown to faculty and stakeholders.
- **Measurable retrieval quality.** Build a test set of 30–50 real faculty questions with known correct sources and measure retrieval + answer quality against it.

## Non-Goals

- **Not official HR advice, and not legal advice.** HOOT is an informational assistant; the actual Temple documents and HR staff remain authoritative.
- **No PII.** HOOT does not connect to individual employee records or collect personal data — it stays purely informational.
- **Nothing behind login.** Only publicly accessible documents are ingested; nothing behind the TUportal login is touched, and `robots.txt` is respected.
- **Not a general-purpose chatbot.** It answers from Temple's document corpus only — it is not a free-form conversational AI.

---

## Target Users

| User Type | Description |
|-----------|-------------|
| Primary User | Temple University faculty asking natural-language questions about HR policy, benefits, research opportunities, and conduct rules. |
| Secondary User | Temple HR / Faculty Affairs staff, who validate accuracy and may provide cleaner source data. |
| Internal User | The OpenOwls student team building, testing, and maintaining the system. |

---

## Tech Stack

HOOT ships in two stages. The **MVP** proves the RAG pipeline works with the least possible ceremony (Streamlit). The **target architecture** — a React frontend on a FastAPI backend — is the committed end state the project is deliberately building toward; the MVP is a stepping stone to it, not a throwaway.

| Layer | MVP (Phase 1–2) | Target (Phase 4+) | Notes |
|-------|-----------------|-------------------|-------|
| UI / Frontend | Streamlit | React 18 | Streamlit gives a working chat box fast; React is the ultimate polished, deployable frontend. |
| Backend / API | (in-process, served by Streamlit) | FastAPI (Python) | RAG logic is written as plain Python modules from day one so it lifts cleanly into a FastAPI service later. |
| RAG framework | Python + LlamaIndex | Python + LlamaIndex | Purpose-built for RAG; carries over unchanged from MVP to target. |
| Vector store | ChromaDB (local) | ChromaDB → Qdrant or Postgres + pgvector | Start with zero-infra local Chroma; graduate only if scale requires it. |
| Embeddings | `BAAI/bge-small-en` (free/local) | same, or OpenAI `text-embedding-3-small` | Local embeddings keep cost at zero for the MVP. |
| LLM | Claude Haiku / GPT-4o-mini | Claude (Anthropic API) | Small + cheap is plenty — retrieval does the heavy lifting. Called server-side only. |
| Evaluation | RAGAS | RAGAS | Added once a test question set exists (Phase 3). |
| Hosting | Streamlit Community Cloud (free) | Vercel (frontend) + Render (backend) | Free tiers throughout. |

> **Architecture note for the team:** Write the ingestion and query pipeline as standalone, framework-agnostic Python (no Streamlit-specific logic inside the RAG core). This is what makes the eventual move from Streamlit to FastAPI + React a frontend swap rather than a rewrite.

---

## Stakeholders

| Name / Role | Responsibility |
|-------------|----------------|
| Faculty Sponsor | Defines scope, reviews milestones, owns `overview.md` and `features.md`. |
| Student Team (OpenOwls) | Design, implementation, evaluation, and deployment. |
| Temple HR / Faculty Affairs | **Recommended to loop in early** — provides accuracy validation, possibly cleaner source data, and goodwill; heads off "is this official?" confusion. |
| Faculty Testers | A few willing faculty who test answers and give feedback in later phases. |

---

## Key Constraints

- **Time:** Should reach a demoable MVP within one semester.
- **Budget:** Free-tier cloud services and free/local models only; no paid infrastructure.
- **Data scope:** Public Temple documents only — respect `robots.txt`, never touch anything behind the TUportal login.
- **Accuracy-critical:** This is HR content. The system must defer ("I couldn't find that in Temple's published documents — contact HR") rather than answer when it is uncertain.
- **Stack direction is fixed:** React + FastAPI is the committed target architecture; the Streamlit MVP must be built so it does not lock the team out of that path.
