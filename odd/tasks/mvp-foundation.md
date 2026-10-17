# Feature: mvp-foundation

Locator: `odd/tasks/mvp-foundation.md` · Engram mirror: `odd/mvp-foundation/tasks`

## Objective

Lay the foundation of Puente, a mobile "first barrier" support assistant for depression for
Spanish-speaking users in Peru: a Flutter app and a Python FastAPI backend with three agents
(empathetic companion, clinical RAG, guardian/judge), daily mood tracking and escalation to a human.

## Problem

People with depressive symptoms often have no one to talk to between the moment they start feeling
bad and the moment they reach a professional. Peru's treatment coverage for depression is low
(~13–25%, INSM studies cited in the research report). A support assistant can accompany, suggest
evidence-based activities, track mood and hand the person off to a human when needed.

## Why this order

The research (`reports/Asistente de salud mental Perú.md`) concludes that safety comes before
empathy: crisis detection must live outside the conversational LLM, be deterministic first, and
fail closed. So the foundation builds the safety path before any LLM is wired in.

## Scope (this feature)

- Repository bootstrap (git, README, AGENTS.md, ignore rules, research moved under `docs/`).
- Backend skeleton: FastAPI app, settings, health endpoint, test setup.
- Guardian layer 1: deterministic crisis lexicon (Peruvian Spanish) and the fixed crisis response
  with Peru resources, behind a fail-closed contract.
- Flutter app skeleton: chat screen shell and an always-visible SOS button that works without the
  backend.

Out of scope here (later features): LLM companion, RAG corpus and retrieval, LLM judge, mood
tracking and PHQ-9/GAD-7, auth and consent, persistence of conversations, voice.

## Constraints

- No diagnosis. The assistant never claims to be a therapist or to diagnose.
- Crisis handling never depends on an LLM being available.
- Crisis resources must be verified against official sources before any real user sees them
  (Línea 113 opción 5 is verified as free and 24/7 via press citing MINSA; WhatsApp channels are not).
- Conversation content is sensitive personal data under Ley 29733 and D.S. 016-2024-JUS: collect
  the minimum, no sensitive content in push notifications or logs.
- Artifacts (code, comments, docs) in English; user-facing copy in neutral Spanish.

## Tasks

- [x] T1 — Repository bootstrap. Route: inline (mechanical files).
- [x] T2 — Backend skeleton (uv, FastAPI, pydantic-settings, `/health`, pytest + ruff). Route: delegated writer (multiple new files).
- [x] T3 — Guardian layer 1: crisis lexicon + fixed crisis response + fail-closed contract, test-first. Route: delegated writer.
- [ ] T4 — Flutter skeleton: chat shell + offline SOS screen with Peru crisis lines. Blocked: Flutter SDK not installed on this machine.

## Acceptance criteria

- `uv run pytest` and `uv run ruff check` pass in `apps/backend`.
- `GET /health` returns 200.
- Any message matching the crisis lexicon returns the fixed crisis response with Peru resources,
  without calling any model; an internal error in the guardian also returns the crisis-safe response.
- The SOS screen opens from every screen and shows crisis lines with tap-to-call, with no network.

## Delivery

Strategy: ask-on-risk. Forecast ~600 authored lines across T2–T4; local repository, no remote yet.

## Progress

- T1: done (see commit log).
- T2: done. Risk tier: medium (new service scaffold, no user data). Commit:
  `feat(backend): scaffold FastAPI service with settings and health endpoint` (hash recorded in
  the T3 entry, since a commit cannot contain its own hash). Observed checks in `apps/backend`:
  - `uv sync`: resolved and installed (fastapi, uvicorn[standard], pydantic-settings, pytest, httpx, ruff).
  - `uv run pytest -q`: 2 passed, 1 warning (Starlette deprecation: `httpx` with TestClient).
  - `uv run ruff check`: All checks passed!
- T2 commit: `71efeeb`.
- T3: done. Risk tier: high (safety-critical crisis path). Commit:
  `feat(guardian): add deterministic crisis lexicon with fail-closed policy and Peru crisis
  resources` (hash: see commit log; a commit cannot contain its own hash). Test-first:
  - RED: `uv run pytest -q` before implementation: 4 collection errors (guardian modules and
    `/v1/messages` missing), 0 tests run.
  - GREEN: `uv run pytest -q`: 57 passed, 1 warning (Starlette `httpx` deprecation).
  - `uv run ruff format` applied before the final check; `uv run ruff check`: All checks passed!
  - `uv sync`: 31 packages, up to date.
  - Notes: crisis response adds a `note` field (CSMC without referral, gob.pe/10942) beyond
    `type/message/resources`. Only Línea 113 opción 5 is `verified=True`; 106, 105, 116 and
    Línea 100 are marked pending confirmation. Lexicon is a seed list pending clinician review.
    Violence-only messages prioritize 105 and Línea 100; any self-risk category or a guardian
    error prioritizes 113 opción 5.

## Next step

T4 Flutter skeleton (blocked until the Flutter SDK is installed). Independent verification of T3
(high tier) recommended before delivery.
