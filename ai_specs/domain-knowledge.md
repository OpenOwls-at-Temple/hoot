# Domain Knowledge

> **OpenOwls SDD** — Read primarily by the AI coding assistant.
> Captures domain-specific concepts, terminology, business rules, and constraints
> that are not obvious from the code itself. Faculty seeds this file; students expand it.

> **⚠️ Verify the specifics:** Temple-specific facts below (the HR phone number `215-204-7174`, the `secretary.temple.edu/policies` domain, category names) are carried over from the project's existing specs. Treat exact URLs, phone numbers, and policy details as **placeholders to confirm with HR / the source sites** before relying on them in production. HOOT's whole premise is not stating facts it can't source — the same discipline applies to this file.

---

## Domain Overview

HOOT operates in the **higher-education HR and policy information** domain. It answers natural-language questions for **Temple University faculty** about benefits, HR policy, conduct rules, and research/funding opportunities — using only Temple's own **publicly published** documents. It is an information-retrieval and grounding system, not a system of record: it holds no individual's data and makes no decisions about any person.

---

## Key Concepts & Terminology

| Term | Definition |
|------|------------|
| **Grounding** | The requirement that every claim in an answer trace back to a retrieved document chunk. Ungrounded text is a defect, not a stylistic choice. |
| **Deferral** | The standard response when the corpus doesn't contain the answer: HOOT says it couldn't find it and directs the user to HR. Deferring correctly is a feature, not a failure. |
| **Citation** | A reference to a source actually used in an answer: `{ title, url, category, last_updated }`. Only used sources appear; never decorative ones. |
| **Chunk** | A section-sized slice of a source document stored in the vector index with metadata. Chunks are the unit of retrieval and citation. |
| **Category** | One of `benefits`, `policy`, `research`, `conduct`. Stored as chunk metadata; shown in citations; optionally used to filter retrieval (Phase 3). |
| **Hybrid retrieval** | Combining dense (embedding) and sparse (BM25 keyword) search, then reranking, so both semantic and exact-term matches (e.g., "FMLA", "Form 1098-T") surface. |
| **Corpus** | The full set of ingested public Temple documents. Defined by what's in `data/` and what ingestion is allowed to fetch. |
| **Benefits** | Compensation-adjacent programs: health insurance, retirement, tuition remission, leave, etc. |
| **Tuition remission** | A benefit reducing tuition for eligible employees/dependents. Notably has **taxability** nuances above IRS limits — a classic "confidently wrong is dangerous" topic. |
| **FMLA** | Family and Medical Leave Act — federal job-protected leave. Eligibility rules are specific; answers must come from the document, not general knowledge. |
| **Faculty Handbook** | A primary source for faculty policy (e.g., outside teaching, tenure). Often lives on a different subdomain than benefits docs. |
| **Code of Conduct** | The source for conduct-category questions (ethics, misconduct, reporting). |
| **Research / funding** | Internal grant, ORS (Office of Research Services)-type, and funding-opportunity information relevant to faculty and some staff/students. |

---

## Business Rules

- **No answer without a source.** If a claim can't be traced to a retrieved chunk, it must not appear in the answer.
- **Defer over guess.** When retrieval finds nothing relevant, or grounding is uncertain, HOOT returns the deferral message and the standard HR contact — it does not fall back to general knowledge.
- **Public documents only.** Nothing behind the TUportal login is ingested or referenced; `robots.txt` is respected at ingestion time.
- **No PII handling.** HOOT does not collect, store, or send to the LLM any personal/employee/student records. It connects to no individual's data.
- **Informational, not authoritative.** Answers are not official HR or legal advice; the underlying Temple documents and HR staff remain the authority. The UI must say so.
- **Don't personalize beyond the document.** HOOT does not know the individual faculty member's tenure status, rank, or appointment type. It answers from the document and lets the source state which conditions apply.
- **Citations reflect actual use.** A source is cited only if it supports a claim in the answer.
- **Freshness is surfaced, not hidden.** Each answer shows the source's `last_updated` date so users can judge currency.

---

## Domain Constraints

- **Context is limited to retrieved chunks.** Only the top-k chunks (start k = 4–6) are ever sent to the LLM — never whole documents, never unrelated categories. See `llm-integration.md`.
- **Embedding consistency.** The same embedding model (`BAAI/bge-small-en`) must be used at ingestion and at query time, or retrieval silently degrades.
- **Section-aware chunking.** Chunk on headings/sections, not fixed character counts, so a policy stays whole and citations point to a coherent passage.
- **Max output ~500 tokens.** Answers are concise and point to the source rather than reproducing it.
- **Coverage applicability varies within faculty.** Many policies apply differently to tenure-track vs. adjunct vs. clinical faculty (e.g., sabbatical eligibility, tuition remission tiers). The answer must reflect what the source says and must not over-generalize across faculty categories.
- **Source documents drift.** Benefits and policy pages change; stale answers are a real risk. Re-ingestion on a schedule is part of correctness, not just hygiene.

---

## Common Pitfalls

- **Taxability nuance.** Statements like "tuition remission is tax-free" are dangerous; the source typically has IRS-limit caveats. Cite the document; don't simplify away the caveat.
- **Over-generalizing within faculty categories.** Answering a tenure-track question with an adjunct-only rule (or vice versa) is a subtle, high-impact error. Anchor to what the cited source actually says about who is covered.
- **Confusing similar policies.** Sick leave vs. FMLA vs. short-term disability; outside teaching vs. consulting/conflict-of-interest. Exact-term retrieval (BM25) matters here.
- **Stale information presented as current.** Always surface `last_updated`; an old date is information, not noise.
- **Treating "no result" as a bug.** Empty retrieval should produce a clean deferral, not a stretched-thin answer from a weakly related chunk.
- **Leaking the HR number wrong.** The deferral contact (`215-204-7174`) and any URLs must be verified — a wrong contact in a deferral undermines the whole "trustworthy" promise.
- **Reproducing long source text verbatim.** Answer in HOOT's own words and link out; don't paste large copyrighted passages.

---

## External Dependencies & Integrations

| Service / Source | Purpose | Notes |
|------------------|---------|-------|
| Temple public policy site (e.g., `secretary.temple.edu/policies`) | Source documents for `policy` / `conduct` | Verify exact paths; respect `robots.txt`. |
| Temple HR / benefits pages | Source documents for `benefits` | Often a different subdomain than policy. |
| Faculty Handbook (public PDF) | Faculty policy source | May live on yet another subdomain. |
| Research / ORS pages | `research` category sources | Funding/grant info relevant mainly to faculty. |
| OpenAI-compatible LLM provider | Grounded answer generation | Server-side only; configured via `LLM_*` env vars. See `llm-integration.md`. |
| `BAAI/bge-small-en` (HuggingFace) | Local embeddings | Same model at ingest + query; downloaded once, runs locally. |
| FlashRank | Reranking retrieved chunks | Local, no external API. |
| RAGAS | Evaluation (Phase 3) | Needs a labeled test set first. |

---

## References

- Temple University policy and HR sites (confirm canonical URLs with the sponsor / HR before ingesting).
- IRS guidance on educational-assistance/tuition benefits (for understanding taxability nuance — **not** to answer from; HOOT answers from Temple's documents only).
- RAGAS documentation (evaluation framework) — see `llm-integration.md` for the metric set and targets.
