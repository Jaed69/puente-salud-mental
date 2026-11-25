"""FastAPI application factory."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI

from puente.api.messages import router as messages_router
from puente.companion.factory import build_chat_model
from puente.config import Settings, get_settings
from puente.knowledge.embeddings import FastEmbedEmbedder, model_spec
from puente.knowledge.retriever import KnowledgeRetriever
from puente.knowledge.store import PgKnowledgeStore, open_pool

logger = logging.getLogger(__name__)

KnowledgeStatus = Literal["disabled", "ready", "unavailable"]


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        pool = None
        if settings.database_url is not None:
            try:
                pool = await open_pool(
                    settings.database_url.get_secret_value(),
                    timeout=settings.database_connect_timeout,
                )
                spec = model_spec(settings.embedding_model)
                embedder = FastEmbedEmbedder(spec, cache_dir=settings.embedding_cache_dir)
                await embedder.warm_up()
                app.state.retriever = KnowledgeRetriever(
                    embedder, PgKnowledgeStore(pool, spec), mode=settings.retrieval_mode
                )
                app.state.knowledge_status = "ready"
            except Exception as exc:
                # The companion keeps working without reference material.
                logger.warning("Knowledge base unavailable (%s).", type(exc).__name__)
                app.state.knowledge_status = "unavailable"
        try:
            yield
        finally:
            if pool is not None:
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
    def ready() -> dict[str, str]:
        status: KnowledgeStatus = app.state.knowledge_status
        return {"status": "ok", "knowledge": status}

    app.include_router(messages_router)
    return app


app = create_app()
