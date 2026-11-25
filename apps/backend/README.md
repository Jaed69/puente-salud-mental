# Puente backend

FastAPI service for Puente. Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+.

## Run

```sh
uv sync
cp .env.example .env   # optional
uv run uvicorn puente.main:app --reload
```

`GET /health` returns `{"status": "ok"}` as soon as the process serves. `GET /ready` reports the
knowledge base: 200 `{"status": "ok", "knowledge": "disabled" | "ready"}`, or 503
`{"status": "degraded", "knowledge": "starting" | "unavailable"}` while it connects. The knowledge
base attaches in the background and retries with backoff (1 s up to 30 s), so the API can start
before the database and before the embedding model is downloaded; meanwhile replies have no
references.

`POST /v1/messages` with `{"text": "...", "history": [{"role": "user"|"assistant", "text": "..."}]}`
(`history` is optional, at most 10 items) runs the guardian (deterministic crisis lexicon,
fail-closed) first. A crisis returns `{"type": "crisis", "message", "resources", "note"}` with a
fixed script and Peru crisis lines, and the model is never called. Otherwise the companion model
answers and the guardian checks its output too: a reply that trips the lexicon becomes the crisis
response. If the model is not configured, fails, times out or returns no text, the reply is a fixed
fallback `{"type": "reply", "message"}`. Message text, history, prompts and model output are never
logged.

When the knowledge base is configured, a non-crisis message first retrieves reference material
(the guardian has already run, so crisis messages never reach retrieval). The model may cite it as
`[n]`; only citations of chunks that were actually retrieved count, markers are removed from the
text, and the reply carries `"sources": [{"source_title", "section_title", "pages", "attribution",
"url"}]`. A reply without valid citations keeps the `{"type": "reply", "message"}` shape. If
retrieval fails or takes longer than `PUENTE_RETRIEVAL_TIMEOUT_SECONDS`, the companion answers
without references. The lexicon in `src/puente/guardian/lexicon.py` is a seed list pending review by Peruvian
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

## Knowledge base

Reference material: the Spanish edition of WHO's "En tiempos de estrés, haz lo que importa"
(CC BY-NC-SA 3.0 IGO, non-commercial; see `corpus/NOTICE.md`). It is stored in PostgreSQL with
pgvector and searched in hybrid mode (vector + Spanish full-text, fused with Reciprocal Rank
Fusion). Embeddings run locally with fastembed: user messages never go to an embedding API.

```sh
docker compose up -d db                      # from the repository root; host port 5433
export PUENTE_DATABASE_URL=postgresql://puente:puente-dev@127.0.0.1:5433/puente
uv run puente-knowledge fetch                # download the PDF and check its SHA-256
uv run puente-knowledge build                # optional: rebuild corpus/chunks from the PDF
uv run puente-knowledge ingest               # load the chunks and embed them
```

The first `ingest` and the first API start download the embedding model (about 2 GB for the
default). Settings: `PUENTE_DATABASE_URL`, `PUENTE_EMBEDDING_MODEL`, `PUENTE_EMBEDDING_CACHE_DIR`,
`PUENTE_RETRIEVAL_MODE` (`hybrid`, `dense` or `lexical`), `PUENTE_RETRIEVAL_K` (default 4),
`PUENTE_RETRIEVAL_TIMEOUT_SECONDS` (default 5) and `PUENTE_DATABASE_CONNECT_TIMEOUT` (default 10).
Without `PUENTE_DATABASE_URL`, or with the database down, the API answers without references.

## Test and lint

```sh
uv run pytest
uv run ruff check
```

Integration tests against PostgreSQL run when `PUENTE_TEST_DATABASE_URL` is set (each test uses a
throwaway schema); otherwise they are skipped:

```sh
PUENTE_TEST_DATABASE_URL=postgresql://puente:puente-dev@127.0.0.1:5433/puente uv run pytest
```
