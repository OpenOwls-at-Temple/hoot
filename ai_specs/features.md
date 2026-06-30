# Features

> **OpenOwls SDD** — Read by end users and the product owner.
> Defines what the application does, written in plain language.
> Organized into three phases. Phase 1 is the MVP — it must be achievable in the first sprint.

---

## How to Read This File

- **Phase 1** — Must-have features. The app is not usable without these.
- **Phase 2** — Should-have features. Adds meaningful value once Phase 1 is stable.
- **Phase 3** — Nice-to-have features. Advanced capabilities, AI enhancements, or stretch goals.

Each feature includes a short description and a set of acceptance criteria written from the user's perspective.

> **Phase 4 (Target Architecture):** The migration from Streamlit to React + FastAPI is tracked as an architectural milestone in `overview.md` and `architecture-planning.md`, not as a user-facing feature here. It re-skins HOOT without changing what it does.

---

## Phase 1 — Core MVP
<!-- The smallest useful version: ask a question, get a cited answer, or an honest "I don't know." -->

### Feature 1: Ask a Question and Get a Grounded Answer
**As a** Temple faculty member,
**I want to** type a plain-language HR/policy question and get a clear answer,
**So that** I don't have to search four separate websites and PDFs myself.

**Acceptance Criteria:**
- [ ] Given the app is loaded, when I type a question and submit, then I receive a concise plain-language answer within a few seconds.
- [ ] Given a question whose answer exists in the corpus, when I submit it, then the answer's content is drawn **only** from retrieved Temple document chunks (no outside knowledge).
- [ ] Given a submitted question, when the system responds, then the answer is at most a few short paragraphs and points me toward the source for detail.

---

### Feature 2: Every Answer Shows Its Sources
**As a** faculty member,
**I want to** see exactly which Temple document(s) an answer came from, with links,
**So that** I can trust the answer and read the authoritative source myself.

**Acceptance Criteria:**
- [ ] Given an answered question, when the answer is shown, then it lists every source actually used, each with a title and a clickable link to the original document.
- [ ] Given a cited source, when it is displayed, then its `category` (benefits / policy / research / conduct) and `last_updated` date are shown.
- [ ] Given an answer, when it is rendered, then no source appears in the citation list unless it actually supports a claim in the answer.

---

### Feature 3: Honest Deferral When the Answer Isn't Found
**As a** faculty member,
**I want to** be told clearly when HOOT doesn't have the answer,
**So that** I'm never misled by a confident but wrong answer on something that affects my employment, benefits, or research.

**Acceptance Criteria:**
- [ ] Given a question with no supporting content in the corpus, when I submit it, then HOOT replies that it couldn't find the answer in Temple's published documents and directs me to HR (215-204-7174).
- [ ] Given retrieval returns no relevant chunks, when the system processes the question, then it returns the deferral message **without** calling the LLM to invent an answer.
- [ ] Given a deferral, when it is shown, then no fabricated citation appears.

---

### Feature 4: Scope & Trust Disclaimer
**As a** faculty member,
**I want to** clearly understand what HOOT is and isn't,
**So that** I don't mistake it for official HR or legal advice.

**Acceptance Criteria:**
- [ ] Given the app loads, when I view it, then a visible disclaimer states HOOT is an informational assistant — not official HR advice, not legal advice, and not authoritative over the actual documents.
- [ ] Given any answer, when it is shown, then the disclaimer remains visible or easily reachable.

---

### Feature 5: Document Ingestion Pipeline *(internal / team-facing)*
**As a** member of the OpenOwls team,
**I want to** load Temple public documents into the searchable index from the command line,
**So that** the assistant has a corpus to answer from and we can refresh it as documents change.

**Acceptance Criteria:**
- [ ] Given documents placed in the `data/` directory, when I run the ingestion command, then they are chunked, embedded, and stored in ChromaDB with metadata (title, source URL, category, last_updated).
- [ ] Given the ingestion runs, when it completes, then re-running it updates the index without manual cleanup of stale state.
- [ ] Given a document is behind a login or disallowed by `robots.txt`, when ingestion runs, then it is **not** ingested.

---

## Phase 2 — Enhanced Features
<!-- Adds value once the core loop is solid. -->

### Feature 6: Conversational Follow-Ups
**As a** faculty member,
**I want to** ask follow-up questions in the same session,
**So that** I can refine my question without retyping context.

**Acceptance Criteria:**
- [ ] Given I've asked a question, when I ask a follow-up, then prior turns in the session are visible as chat history.
- [ ] Given a follow-up, when it is answered, then the grounding and citation rules from Phase 1 still apply to every turn.

---

### Feature 7: Answer Feedback (Thumbs Up / Down)
**As a** faculty member,
**I want to** flag whether an answer was helpful or wrong,
**So that** the team can find weak spots and improve retrieval.

**Acceptance Criteria:**
- [ ] Given an answer, when I rate it up or down, then the rating is recorded with the question and the sources shown (no PII).
- [ ] Given negative feedback, when it is recorded, then the team can review flagged questions to grow the evaluation set.

---

### Feature 8: Source Preview & Freshness Signals
**As a** faculty member,
**I want to** preview the relevant passage and see how recently the source was updated,
**So that** I can judge whether the information is current.

**Acceptance Criteria:**
- [ ] Given a cited source, when I expand it, then I can see the specific retrieved passage the answer relied on.
- [ ] Given a source with an old `last_updated` date, when it is shown, then the staleness is visible (e.g., the date is displayed prominently).

---

### Feature 9: Scheduled Re-Ingestion for Freshness
**As a** member of the OpenOwls team,
**I want to** refresh the corpus on a schedule,
**So that** benefits and policy changes are reflected without manual effort each time.

**Acceptance Criteria:**
- [ ] Given a configured schedule, when it triggers, then ingestion re-runs and updates changed documents.
- [ ] Given a re-ingestion, when it completes, then `last_updated` dates in citations reflect the refreshed corpus.

---

## Phase 3 — Advanced / AI Features
<!-- AI enhancements and measurement. -->

### Feature 10: Question Category Routing
**As a** faculty member,
**I want** HOOT to focus retrieval on the right topic area for my question,
**So that** I get more precise answers, especially when topics overlap.

**Acceptance Criteria:**
- [ ] Given a question, when it is processed, then it is classified into one of `benefits` / `policy` / `research` / `conduct` (or `unknown`).
- [ ] Given a confident classification, when retrieval runs, then it can be filtered to that category to improve precision.
- [ ] Given an `unknown` classification, when retrieval runs, then it falls back to searching all categories (Phase 1 behavior).

---

### Feature 11: Retrieval Quality Evaluation (RAGAS)
**As a** member of the OpenOwls team,
**I want to** measure retrieval and answer quality against a labeled test set,
**So that** we can prove HOOT works and catch regressions.

**Acceptance Criteria:**
- [ ] Given a test set of 30–50 real questions with known correct sources, when the evaluation runs, then it reports retrieval hit rate, faithfulness, citation correctness, deferral correctness, JSON parse rate, and response time.
- [ ] Given results, when they are reported, then metrics are broken out **per category** so weak areas are visible.
- [ ] Given the targets in `llm-integration.md`, when results are below target, then the failing metric is clearly identifiable.

---

### Feature 12: Optional Temple-Community Access Gate
**As a** project maintainer,
**I want** the option to restrict HOOT to signed-in Temple accounts,
**So that** we can control abuse and cost without changing what data is served.

**Acceptance Criteria:**
- [ ] Given the gate is enabled, when an unauthenticated user arrives, then they are asked to sign in with a Temple Google (@temple.edu) account before asking questions.
- [ ] Given the gate is disabled (MVP default), when a user arrives, then they can ask questions without signing in.
- [ ] Given sign-in is used, when a user authenticates, then **no** new personal data is collected or stored beyond what's needed for the session. (See `auth-security.md`.)

---

## Out of Scope
<!-- Explicitly excluded to prevent scope creep. -->

- Any access to records behind the TUportal login (employee records, individual benefits enrollment, payroll, etc.).
- Personalized answers based on a specific individual's records or role.
- Mobile native app (web only for now).
- Multi-language support (English only for the MVP).
- Free-form general-purpose chat unrelated to Temple's document corpus.
- Write actions of any kind — HOOT is read-only and never changes Temple systems.
