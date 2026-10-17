# Puente backend

FastAPI service for Puente. Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

## Run

```sh
uv sync
cp .env.example .env   # optional
uv run uvicorn puente.main:app --reload
```

`GET /health` returns `{"status": "ok"}`.

## Test and lint

```sh
uv run pytest
uv run ruff check
```
