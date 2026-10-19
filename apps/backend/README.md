# Puente backend

FastAPI service for Puente. Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

## Run

```sh
uv sync
cp .env.example .env   # optional
uv run uvicorn puente.main:app --reload
```

`GET /health` returns `{"status": "ok"}`.

`POST /v1/messages` with `{"text": "...", "history": [{"role": "user"|"assistant", "text": "..."}]}`
(`history` is optional, at most 10 items) runs the guardian (deterministic crisis lexicon,
fail-closed) first. A crisis returns `{"type": "crisis", "message", "resources", "note"}` with a
fixed script and Peru crisis lines, and the model is never called. Otherwise the companion model
answers and the guardian checks its output too: a reply that trips the lexicon becomes the crisis
response. If the model is not configured, fails, times out or returns no text, the reply is a fixed
fallback `{"type": "reply", "message"}`. Message text, history, prompts and model output are never
logged. The lexicon in `src/puente/guardian/lexicon.py` is a seed list pending review by Peruvian
clinicians.

## Companion model

One adapter talks to any OpenAI-compatible `/chat/completions` endpoint. Set these in `.env`:

| Provider | `PUENTE_LLM_BASE_URL` | `PUENTE_LLM_MODEL` example |
|----------|-----------------------|----------------------------|
| OpenRouter (free models) | `https://openrouter.ai/api/v1` | any id ending in `:free` |
| Cloudflare Workers AI | `https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/ai/v1` | `@cf/meta/llama-3.1-8b-instruct` |
| Groq | `https://api.groq.com/openai/v1` | a model from the Groq console |
| Gemini (paid or free tier) | `https://generativelanguage.googleapis.com/v1beta/openai/` | a Gemini model id |

Also set `PUENTE_LLM_API_KEY`; optional: `PUENTE_LLM_TIMEOUT_SECONDS` (default 20) and
`PUENTE_LLM_MAX_OUTPUT_TOKENS` (default 300).

**Privacy:** free tiers may log prompts or use them for training. Demo with synthetic data only and
never connect real users to a free tier. Conversation content is sensitive personal data under
Ley 29733.

## Test and lint

```sh
uv run pytest
uv run ruff check
```
