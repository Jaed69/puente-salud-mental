"""FastAPI application factory."""

import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from puente.api.messages import router as messages_router
from puente.companion.factory import build_chat_model
from puente.config import Settings, get_settings
from puente.knowledge.embeddings import FastEmbedEmbedder, model_spec
from puente.knowledge.retriever import KnowledgeRetriever
from puente.knowledge.store import PgKnowledgeStore, open_pool

logger = logging.getLogger(__name__)

KnowledgeStatus = Literal["disabled", "starting", "ready", "unavailable"]

ATTACH_RETRY_INITIAL_SECONDS = 1.0
ATTACH_RETRY_MAX_SECONDS = 30.0


async def attach_knowledge(app: FastAPI, settings: Settings) -> Any | None:
    """Try once to connect the knowledge base. Returns the open pool, or ``None`` on failure."""
    if settings.database_url is None:
        return None
    pool = None
    try:
        pool = await open_pool(
            settings.database_url.get_secret_value(), timeout=settings.database_connect_timeout
        )
        spec = model_spec(settings.embedding_model)
        embedder = FastEmbedEmbedder(spec, cache_dir=settings.embedding_cache_dir)
        await embedder.warm_up()
    except Exception as exc:
        logger.warning("Knowledge base unavailable (%s).", type(exc).__name__)
        if pool is not None:
            await pool.close()
        app.state.knowledge_status = "unavailable"
        return None
    app.state.retriever = KnowledgeRetriever(
        embedder, PgKnowledgeStore(pool, spec), mode=settings.retrieval_mode
    )
    app.state.knowledge_status = "ready"
    return pool


async def _keep_attaching(app: FastAPI, settings: Settings, pools: list[Any]) -> None:
    """Retry with exponential backoff until the knowledge base attaches."""
    delay = ATTACH_RETRY_INITIAL_SECONDS
    while True:
        pool = await attach_knowledge(app, settings)
        if pool is not None:
            pools.append(pool)
            return
        await asyncio.sleep(delay)
        delay = min(delay * 2, ATTACH_RETRY_MAX_SECONDS)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # The knowledge base attaches in the background: the database may start after the API,
        # and the first start downloads the embedding model. The companion answers without
        # references meanwhile.
        pools: list[Any] = []
        task = None
        if settings.database_url is not None:
            app.state.knowledge_status = "starting"
            task = asyncio.create_task(_keep_attaching(app, settings, pools))
        try:
            yield
        finally:
            if task is not None:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task
            for pool in pools:
                await pool.close()

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.settings = settings
    app.state.chat_model = build_chat_model(settings)
    app.state.retriever = None
    app.state.knowledge_status = "disabled"

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> JSONResponse:
        """200 when the configured knowledge base serves (or none is configured), else 503."""
        knowledge: KnowledgeStatus = app.state.knowledge_status
        if knowledge in ("disabled", "ready"):
            return JSONResponse({"status": "ok", "knowledge": knowledge})
        return JSONResponse({"status": "degraded", "knowledge": knowledge}, status_code=503)

    app.include_router(messages_router)
    return app


app = create_app()
