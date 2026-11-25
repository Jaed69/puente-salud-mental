# Puente

A mobile "first barrier" support assistant for depression, for Spanish-speaking users in Peru.
It listens, suggests evidence-based activities, tracks mood over time and hands the person off to a
human (crisis lines, community mental-health centres, psychologists) when needed.

> Puente does not diagnose and is not a therapist. In a crisis in Peru, call **Línea 113, opción 5**
> (MINSA, free, 24/7) or **106** (SAMU).

## Architecture (target)

- **App:** Flutter (text first, voice later).
- **Backend:** Python, FastAPI, PostgreSQL + pgvector.
- **Agents:** empathetic companion, clinical RAG grounded on licensed lay material, and a guardian
  that checks every user message and every reply. Crisis detection is deterministic first and never
  depends on an LLM being available.

## Run it locally

Requires Docker. From the repository root:

```sh
docker compose up -d --build     # db + one-shot knowledge ingestion + API
curl http://127.0.0.1:8000/ready # 503 "starting" until the embedding model is downloaded
```

- The API listens on `http://127.0.0.1:8000` (`POST /v1/messages`). Set `PUENTE_API_BIND=0.0.0.0`
  to reach it from a phone on the same network.
- To get real replies, configure the companion model in `apps/backend/.env` (see
  `apps/backend/README.md`). Without it the API serves a fixed fallback reply. The guardian and
  the crisis response work either way.
- Without Docker, run the backend with uv (`apps/backend/README.md`) and the app with Flutter
  (`apps/mobile/README.md`).

## What works today

- Guardian layer 1: deterministic crisis detection on every message and every reply. It fails
  closed and returns Peru crisis lines.
- Companion: any OpenAI-compatible chat model, behind the guardian.
- Clinical RAG: WHO's "En tiempos de estrés, haz lo que importa" (Spanish, CC BY-NC-SA 3.0 IGO),
  with local embeddings and hybrid search on PostgreSQL + pgvector. Replies cite their sources, and
  the backend checks every citation. See `apps/backend/eval/reports/` for the retrieval
  evaluation.
- Flutter app: chat, crisis card with tap-to-call, offline SOS screen.

## Layout

- `apps/backend` — FastAPI service.
- `apps/mobile` — Flutter app.
- `docs/research` — research report and notes behind the design decisions.
- `odd/tasks` — feature documents with tasks, checks and progress.
