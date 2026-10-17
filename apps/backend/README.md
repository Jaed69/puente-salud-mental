# Puente backend

FastAPI service for Puente. Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

## Run

```sh
uv sync
cp .env.example .env   # optional
uv run uvicorn puente.main:app --reload
```

`GET /health` returns `{"status": "ok"}`.

`POST /v1/messages` with `{"text": "..."}` runs the guardian (deterministic crisis lexicon,
fail-closed) first. A crisis returns `{"type": "crisis", "message", "resources", "note"}` with a
fixed script and Peru crisis lines; otherwise a placeholder reply (no LLM yet). Message text is
never logged. The lexicon in `src/puente/guardian/lexicon.py` is a seed list pending review by
Peruvian clinicians.

## Test and lint

```sh
uv run pytest
uv run ruff check
```
