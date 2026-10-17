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

## Layout

- `apps/backend` — FastAPI service.
- `apps/mobile` — Flutter app.
- `docs/research` — research report and notes behind the design decisions.
- `odd/tasks` — feature documents with tasks, checks and progress.
