# Authentication & Security

> **OpenOwls SDD** — Read by engineers and the AI coding assistant.
> Defines how users are authenticated and authorized, how sensitive data is protected,
> and what security rules apply across the project. Security is a design concern, not a
> last-minute checklist — document these decisions before writing auth code.

---

## Security Posture for HOOT (read this first)

HOOT is a **public, read-only, no-PII** information tool. It serves only publicly available Temple documents, stores no user records, and makes no changes to any system. That reshapes what "secure" means here:

- There is **no user data to protect**, so the MVP needs **no login, no passwords, no JWTs, no user database**. Building those would add attack surface and maintenance for zero benefit.
- The security work that actually matters for HOOT is: **protecting the LLM API key**, **resisting prompt injection**, **not leaking or logging anything a user happens to type**, **safe ingestion** (respecting `robots.txt`, no SSRF), **safe rendering** of model output, and **abuse/cost control** (rate limiting).
- An **optional** "sign in with Temple Google account" gate exists as a Phase 4 feature — for **abuse and cost control**, not data protection, since the underlying data is public.

The sections below are filled in against this reality. Where the generic template assumes account machinery that HOOT doesn't have, that's stated explicitly rather than invented.

---

## User Model & Scale

| Question | Decision |
|----------|----------|
| Expected number of users | Hundreds — Temple's faculty body. Design for hundreds, not thousands. |
| Growth expectation | Roughly flat; bounded by the faculty headcount. No viral scaling. |
| User model | Multi-user, single-tenant — all faculty share one application instance and one corpus. |
| Do users belong to groups? | No app-enforced groups. All users are faculty; policy nuances (tenure-track vs. adjunct, etc.) are stated in the cited document, not enforced by HOOT. |
| Anonymous / guest access? | **Yes (MVP).** Corpus is public-facing, so anonymous use is allowed. An optional Temple-account gate can be enabled later (Phase 4). |

---

## Identity Strategy

| Setting | Decision |
|---------|----------|
| Approach | **MVP: none** (anonymous public access). **Optional Phase 4: third-party OAuth.** |
| Why this approach | Data is public and no PII is stored, so login is unnecessary for the MVP. If abuse or cost becomes a problem, an SSO gate restricts use to the Temple community without changing the data served. |
| Identity provider(s) | *(If gated)* Google Workspace SSO restricted to `@temple.edu` accounts. |
| Fallback / alternative | None. The gate is all-or-nothing; if disabled, access is anonymous. No roll-your-own passwords are ever introduced. |

---

## Authentication Method

| Setting | Value |
|---------|-------|
| Method | **MVP: none.** *(Optional Phase 4: Google OAuth via the provider's SDK — HOOT never sees or stores a password.)* |
| Why this method | OAuth with Google avoids storing any credentials; it only confirms the visitor holds a Temple account. HOOT never rolls its own password system. |
| Token storage (client) | *(If gated)* short-lived session via an httpOnly cookie — never `localStorage`. |
| Token lifetime | *(If gated)* short session (e.g., a few hours); re-auth on expiry. No long-lived refresh tokens are needed for a read-only tool. |
| Password hashing | **N/A** — HOOT stores no passwords, ever. |

---

## Authorization & Roles

| Role | Permissions |
|------|-------------|
| Visitor (anonymous or signed-in faculty) | Ask questions; read grounded answers and citations. Read-only. Identical access for all users. |
| Maintainer (OpenOwls team) | Runs the **ingestion pipeline** and deployments. This is an **operational** role exercised via the repo/CLI and hosting dashboards — **not** an in-app admin login. |
| Feedback reviewer *(Phase 2/3, optional)* | Reviews aggregated, de-identified thumbs-up/down feedback to improve retrieval. No access to anything else. |

- **Enforcement point:** For the MVP there is nothing to authorize beyond "the app is public." If the access gate is enabled, the sign-in check is enforced **server-side** (FastAPI), never trusted from the frontend.
- **Default posture:** Read-only by design. There are **no** state-changing user-facing routes to protect — HOOT cannot write to any Temple system.

---

## User Lifecycle & Management

| Stage | Decision |
|-------|----------|
| Account creation | **N/A (MVP)** — no accounts. *(If gated: identity is provided entirely by Google; HOOT provisions nothing.)* |
| Onboarding | None. Users land directly on the ask box plus the scope disclaimer. |
| Password reset | **N/A** — no passwords. (SSO handles its own recovery.) |
| Account recovery | **N/A** — HOOT holds no account to recover. |
| Profile updates | **N/A** — no profiles stored. |
| Deactivation / deletion | **N/A** — nothing to delete because nothing personal is stored. |
| Who administers users | No one — there are no user records to administer. The team administers the **corpus and deployment**, not users. |

---

## Sensitive Data

| Data | Classification | Protection |
|------|---------------|------------|
| LLM API key (`LLM_API_KEY`) | Secret | Server-side environment variable only; never committed, never sent to the client. The single most important secret in the system. |
| User question text | Potentially user-volunteered PII | HOOT doesn't ask for PII, but a faculty member might type some. Don't persist raw questions with identifying detail; if questions are logged for eval, scrub or aggregate. Never send anything beyond the question + retrieved chunks to the LLM. |
| Ingested documents | Public | Corpus is public-facing. No special protection needed, but ingestion must confirm a source is public before indexing it. |
| Feedback records *(Phase 2/3)* | De-identified | Store rating + question + sources only; no user identity. |

> HOOT collects **no** passwords, employee records, or account data — there is nothing of that kind in the system to leak.

---

## Secrets Management

- All secrets live in environment variables, never in committed code.
- `.env` files are git-ignored; a `.env.example` with dummy values is checked in.
- Each environment (local, staging, production) uses separate secrets / keys.
- Rotate any secret immediately if it is accidentally committed.
- The LLM key lives only where server-side code runs (Streamlit host secrets, or Render env vars in the target) — never in frontend/browser code.

---

## Common Web Vulnerabilities

| Threat | Mitigation |
|--------|------------|
| **Prompt injection** (most relevant to HOOT) | Treat retrieved chunks and user input as untrusted. The system prompt forbids following instructions found in context and forbids using outside knowledge. Validate the model's JSON shape; on anomaly, default to deferral. Never let model output trigger actions — HOOT has no actions to trigger. |
| Cross-site scripting (XSS) | Escape/sanitize model output and citation fields before rendering. In React, rely on default escaping and avoid `dangerouslySetInnerHTML`; in Streamlit, avoid unsafe HTML rendering of model text. |
| Server-side request forgery (SSRF) during ingestion | Ingestion fetches URLs — restrict to an allowlist of Temple domains, respect `robots.txt`, and never fetch arbitrary user-supplied URLs at query time. |
| SQL injection | Largely **N/A** — no SQL database in the MVP (ChromaDB). If pgvector is adopted later, use parameterized queries / the ORM only. |
| Broken access control | Minimal surface (read-only, public). If the access gate is added, enforce the sign-in check server-side on every protected route. |
| Sensitive data exposure | Enforce HTTPS everywhere; never return the LLM key or any secret in responses; don't echo back logged questions. |
| Denial-of-wallet / abuse | Rate-limit requests (per IP/session) so a flood of questions can't run up LLM cost or exhaust free-tier quotas. |

---

## Input Validation

- Validate every question server-side even if the UI also validates.
- Enforce a **length cap** on questions (reject very long inputs that inflate token cost or attempt injection padding).
- In the target FastAPI backend, validate request bodies with **Pydantic schemas** and reject unexpected fields.
- Sanitize model output and retrieved metadata before rendering (see XSS above).
- Reject or safely handle non-text input; HOOT only accepts a text question.

---

## Session & Account Safety

- **Rate-limit** by IP/session to prevent abuse and runaway cost; surface a "try again in a moment" message when limits are hit.
- *(If the access gate is enabled)* invalidate the session on sign-out and on expiry; keep sessions short.
- No password/refresh-token rotation rules apply because HOOT has no passwords or long-lived tokens.
- Monitor LLM spend/quota; alert the team if usage spikes.

---

## Security Checklist Before Deploy

- [ ] No secrets in the repository or in frontend code (`LLM_API_KEY` server-side only).
- [ ] HTTPS enforced in staging and production.
- [ ] Prompt-injection guardrails in place: context is untrusted, outside knowledge forbidden, JSON validated, defer-by-default.
- [ ] Model output and citation fields are escaped/sanitized before rendering.
- [ ] Ingestion restricted to allowlisted public Temple domains; `robots.txt` respected; nothing behind login ingested.
- [ ] Rate limiting active to control abuse and LLM cost.
- [ ] No raw user questions logged with identifying detail.
- [ ] Dependencies checked for known vulnerabilities.
- [ ] Error messages don't leak stack traces, secrets, or internal details to users.

---

## What Claude Code Should Never Do

- Never put `LLM_API_KEY` (or any secret) in client-side code, the repository, or model output.
- Never send PII, employee/student records, or login-gated content to the LLM — only the question and retrieved **public** chunks.
- Never log passwords (there are none), tokens, or raw user questions containing PII.
- Never let the model answer from outside the retrieved context, and never let instructions embedded in a document chunk or user message override the grounding/deferral rules.
- Never ingest content behind the TUportal login or disallowed by `robots.txt`.
- Never add a password-based auth system or a user database "to be safe" — it adds risk HOOT's design specifically avoids. If auth is needed, use the SSO gate described above and ask first.
