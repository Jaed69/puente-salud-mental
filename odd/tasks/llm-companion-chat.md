# Feature: llm-companion-chat

Locator: `odd/tasks/llm-companion-chat.md` · Engram mirror: `odd/llm-companion-chat/tasks`
Branch: `feat/llm-companion-chat`

## Objective

Replace the placeholder reply with a real LLM companion, reachable from the Flutter chat, while
keeping the deterministic guardian in front of and behind every model call.

## Problem

The chat shell answers with a fixed local placeholder and never calls the backend. The backend
answers with a fixed placeholder too. Nothing demonstrates the AI integration yet.

## Why

Delivery 1 of the plan agreed with the user (2026-10-16): a working demo of chat with real AI,
needed quickly for an internship application (Flutter + Python + LLM integration).

## Scope

- Backend: a `ChatModelPort` and one OpenAI-compatible chat adapter, configured by environment
  (base URL, API key, model). One adapter covers free tiers such as OpenRouter free models and
  Cloudflare Workers AI, and paid providers, so models stay swappable.
- Backend: companion service with a safety system prompt; guardian layer 1 on the input (existing)
  and on the model output; fixed non-LLM fallback when the model fails, times out or is not
  configured.
- Mobile: chat calls `POST /v1/messages`, renders replies, renders crisis responses with the
  crisis resources and tap-to-call, and falls back gracefully offline.
- Docs: provider setup and the privacy caveat of free tiers.

Out of scope: persistence, auth, long-term memory, LLM judge (layers 2–3), RAG, voice, on-device
models.

## Constraints

- Crisis detection and the crisis response never depend on an LLM; guardian fails closed.
- No diagnosis; the assistant never presents itself as a therapist.
- Never log message text or model output (Ley 29733).
- Free LLM tiers may log or train on prompts: demo with synthetic data only, never real users.
- Code, comments and docs in English; user-facing copy in neutral Spanish.
- Tests never call a real model or the network.

## Tasks

- [x] T1 — Backend companion: port, OpenAI-compatible adapter, companion service, output guard,
  fallback, settings, tests. Route: delegated writer (several non-trivial files).
- [x] T2 — Mobile: backend client, chat wired to `/v1/messages`, crisis rendering, offline
  fallback, tests. Route: delegated writer (several non-trivial files).
- [ ] T3 — (done except `apps/backend/.env.example`, blocked by permission settings) Docs: provider setup (OpenRouter, Cloudflare Workers AI, others) and privacy caveat.
  Route: inline or folded into T1/T2 writers.

## Acceptance criteria

- `uv run pytest` and `uv run ruff check` pass in `apps/backend`; `flutter test` and
  `flutter analyze` pass in `apps/mobile`.
- A non-crisis message returns the model reply; a crisis message returns the crisis response
  without calling the model; a model reply that trips the lexicon is replaced by the crisis
  response; a model error or missing configuration returns the fixed fallback reply.
- The app shows replies from the backend and crisis responses with tap-to-call resources.

## Delivery

Strategy: ask-on-risk (decide PR slicing when the user asks for a PR). Forecast ~600 authored
lines across T1–T3. Remote: `origin` = github.com/Jaed69/puente-salud-mental (private).

## Progress

- 2026-10-16: repository created on GitHub (private) and `main` pushed; branch created.
- T1 done in commit `1caa084` (delegated writer).
  - Added `puente/companion/` (port, OpenAI-compatible httpx adapter, service, factory), settings
    `PUENTE_LLM_*`, an async endpoint, the guardian on input and output, a fixed fallback and a
    bounded `history` (max 10).
  - RED: `uv run pytest -q`: 4 collection errors (missing companion modules, `COMPANION_FALLBACK`).
  - GREEN: `uv run pytest -q`: 114 passed. `uv run ruff check`: All checks passed!
    `uv run ruff format --check`: 23 files already formatted.
  - Parent spot check: `uv run pytest -q`: 114 passed.
  - Risk: medium (configuration change, slice budget reached). Native review granted; lineage
    `review-8d0c04b19e77ec8b` approved and acknowledged. Reviewed boundary is now `1caa084`.
  - T3 backend docs are done in `apps/backend/README.md`.
  - Pending: `apps/backend/.env.example` could not be written (permission settings deny the
    write). The proposed content is in the T1 handoff.
  - Follow-ups:
    - Output-triggered crisis uses the output's categories, so a violence-only match shows the
      violence script.
    - httpx INFO logs include the request URL (for Cloudflare it contains the account id); no
      body is logged.

- T2 done in commit `ba964ec` (delegated writer).
  - Added a `CompanionApi` HTTP client (`PUENTE_API_BASE_URL`, default `http://10.0.2.2:8000`,
    30 s timeout, history bounded to 10, UTF-8 decoding from bytes).
  - Added typed reply/crisis models and a crisis card with tap-to-call that opens SOS. A malformed
    crisis payload falls back to the bundled crisis resources (fail closed).
  - Added a loading state and an offline fallback message.
  - Android: INTERNET permission in the main manifest; cleartext HTTP in the debug build only.
  - Updated the mobile README.
  - RED: `flutter test`: the 2 new chat test files failed to load; 9 SOS tests passed.
  - GREEN: `flutter analyze`: No issues found! `flutter test`: 40 passed. `dart format .`: 0
    changed.
  - Parent spot check: `flutter test`: All tests passed (40).
  - Risk: medium (executable change in the debug manifest, slice budget reached). Native review
    granted; lineage `review-3daf7ac074f6cec9` approved and acknowledged. Reviewed boundary is now
    `ba964ec`.
  - Size: about 1,259 changed lines in the slice, roughly half of them tests (planning heuristic
    only).
  - Follow-ups:
    - The backend has no CORS, so the Flutter web build always shows the fallback.
    - A physical device needs the backend started with `--host 0.0.0.0`.

## Next step

Apply `apps/backend/.env.example` (needs user permission or a manual edit). Then push the branch
and open a PR (the user decides), and start delivery 2: Postgres, Docker Compose and auth.
