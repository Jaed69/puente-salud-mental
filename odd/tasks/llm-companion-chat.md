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

- [ ] T1 — Backend companion: port, OpenAI-compatible adapter, companion service, output guard,
  fallback, settings, tests. Route: delegated writer (several non-trivial files).
- [ ] T2 — Mobile: backend client, chat wired to `/v1/messages`, crisis rendering, offline
  fallback, tests. Route: delegated writer (several non-trivial files).
- [ ] T3 — Docs: provider setup (OpenRouter, Cloudflare Workers AI, others) and privacy caveat.
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

## Next step

T1 — backend companion.
