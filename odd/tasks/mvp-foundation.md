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
- [x] T4 — Flutter skeleton: chat shell + offline SOS screen with Peru crisis lines. Route: delegated writer (multiple new files).

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
- T3 review follow-up: review lineage `review-02f673ddef0a33d8` approved with 3 advisories, all
  fixed in commit `fix(guardian): keep crisis detection across sentence boundaries and fail closed
  when building the crisis response`. Risk tier: high (safety path).
  - Advisory 1 (false negative): `detect` now also matches each clause split at sentence
    boundaries (`. ! ? ; : … ¡ ¿` and newlines) on the raw text, so "acabar con todo. La vida..."
    is detected while "acabar con todo el trabajo" still is not.
  - Advisory 2: test pins that VIOLENCE plus a self-risk category uses the general script with
    Línea 113 opción 5 first.
  - Advisory 3: crisis response construction in `/v1/messages` fails closed to a static literal
    payload (113 opción 5 and 106, type `crisis`); only the exception type is logged.
  - RED: `uv run pytest -q` with the new tests: 10 failed, 58 passed (9 punctuation-separated
    crisis statements, 1 builder-failure API test; the advisory 2 pin passes by design since it
    fixes current behavior).
  - GREEN: `uv run pytest -q`: 68 passed, 1 warning (Starlette `httpx` deprecation).
  - `uv run ruff format`: 15 files left unchanged; `uv run ruff check`: All checks passed!
- T4: done. Risk tier: high (SOS is a safety path). Commit: `feat(mobile): scaffold Flutter app
  with chat shell and offline SOS screen` (hash: see commit log). Flutter 3.47.7 / Dart 3.13.5;
  `flutter create --platforms android,ios,web`, plus `url_launcher`. ~660 authored lines in
  `lib/`, `test/` and README (generated platform files excluded); over the 400 heuristic because
  the tests cover every SOS acceptance case.
  - `lib/features/sos/crisis_resources.dart` mirrors the backend resources (same order, ids and
    `verified` flags; only 113 opción 5 verified; no WhatsApp). SOS opens from an AppBar action
    "Ayuda ahora" with no network call; tap-to-call uses an injected `PhoneLauncher`
    (`tel:113` for 113 opción 5, with "luego marca 5"); a failed or throwing launch shows the
    number as `SelectableText` and a SnackBar.
  - Chat shell appends the user message and a fixed local placeholder reply; blank input does
    not send; disclaimer line visible.
  - RED: `flutter test` before implementation: 2 test files failed to load (`PuenteApp`,
    `SosScreen`, `crisisResources`, `ChatScreen` undefined), 0 tests passed.
  - GREEN: `flutter test`: 12 passed (All tests passed!).
  - `flutter pub get`: Got dependencies. `dart format .`: 7 files (3 changed) before final
    checks. `flutter analyze`: No issues found!
  - Not run: Android/iOS builds (no Android SDK on this machine; iOS needs macOS).
- Review of T3 follow-up + T4: lineage `review-9ab45fe626dfabf6` approved and acknowledged with
  one advisory (static crisis payload could drift from `CrisisOut`). Fixed with a contract test
  that validates `STATIC_CRISIS_PAYLOAD` against `CrisisOut` and the canonical resources. The test
  pins current behavior, so it passed on first run (no RED). `uv run pytest -q`: 69 passed;
  `uv run ruff check`: All checks passed! Parent spot check: `flutter test`: 12 passed.

## Next step

Wire the chat to the backend `/v1/messages` (crisis responses rendered with the SOS resources),
then the next feature: LLM companion plus guardian layers 2–3. Confirm the pending crisis numbers
and have Peruvian clinicians review the lexicon before any real user.
