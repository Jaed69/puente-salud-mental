# Puente backend: FastAPI API and the knowledge CLI (puente-knowledge).
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PUENTE_EMBEDDING_CACHE_DIR=/models

COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv

WORKDIR /app

# Dependencies first, so code changes do not reinstall them.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
COPY corpus/chunks ./corpus/chunks
COPY corpus/NOTICE.md ./corpus/NOTICE.md
RUN uv sync --frozen --no-dev

RUN useradd --create-home --uid 10001 puente \
    && mkdir -p /models \
    && chown puente:puente /models
USER puente

EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["uvicorn", "puente.main:app", "--host", "0.0.0.0", "--port", "8000"]
