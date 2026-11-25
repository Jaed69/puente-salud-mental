"""MCP server: Puente's guardian and knowledge base as tools for any model.

An inbound adapter, like the HTTP API: whoever connects brings their own model, and Puente
contributes the deterministic crisis check, the Peru crisis resources and the WHO guidance search.

Safety boundary: over MCP the client model decides when to call a tool, so the guardian is
advisory here. The server instructions ask the model to check every message, and
``search_guidance`` checks its query before retrieving anything; only the Puente app (HTTP API)
enforces the guardian on every turn.

Message text is sensitive personal data (Peru Ley 29733): nothing here logs it.
"""

import asyncio
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Annotated, Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field, StringConstraints

from puente.companion.grounding import format_pages
from puente.config import Settings, get_settings
from puente.guardian.policy import CrisisResponse, build_crisis_response, safe_assess
from puente.guardian.resources import (
    COMMUNITY_MENTAL_HEALTH_NOTE,
    CRISIS_RESOURCES,
    CrisisResource,
    ResourceNote,
)
from puente.knowledge.ports import RetrieverPort

logger = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 4000
MAX_RESULTS = 10

RetrieverFactory = Callable[[], Awaitable[RetrieverPort]]

Text = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_TEXT_LENGTH)
]

INSTRUCTIONS = """\
Puente supports Spanish-speaking people in Peru who feel stressed or low. It does not diagnose
and is not a therapist.

Call check_message on every message the person writes, before you answer. When it returns
risk "crisis", show its crisis_response message and resources to the person, encourage them to
call now, and do not continue the conversation as usual.

Use search_guidance for evidence-based self-help from the WHO guide "En tiempos de estrés, haz
lo que importa". Base your advice on the returned text, cite the section and pages, and show the
attribution: the material is CC BY-NC-SA 3.0 IGO and may only be used non-commercially.

Only resources marked verified have been confirmed against an official source."""

LICENSE_NOTE = (
    "WHO material licensed CC BY-NC-SA 3.0 IGO: non-commercial use only, show the attribution, "
    "and share adaptations under the same licence."
)

READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=False)


class MessageCheck(BaseModel):
    risk: Literal["none", "crisis"]
    categories: list[str]
    crisis_response: CrisisResponse | None


class GuidanceResult(BaseModel):
    rank: int
    source_title: str
    section_title: str
    pages: str
    text: str
    attribution: str
    url: str


class GuidanceSearch(BaseModel):
    crisis_response: CrisisResponse | None
    results: list[GuidanceResult]
    license_note: str


class CrisisResources(BaseModel):
    resources: list[CrisisResource]
    note: ResourceNote


class LazyRetriever:
    """Connects on first use, so the guardian tools work even when the database is down.

    A failed connection is not cached: the next search tries again.
    """

    def __init__(self, factory: RetrieverFactory) -> None:
        self._factory = factory
        self._retriever: RetrieverPort | None = None
        self._lock = asyncio.Lock()

    async def get(self) -> RetrieverPort:
        async with self._lock:
            if self._retriever is None:
                self._retriever = await self._factory()
            return self._retriever


def _check(text: str) -> MessageCheck:
    decision = safe_assess(text)
    if decision.risk == "crisis":
        return MessageCheck(
            risk="crisis",
            categories=list(decision.categories),
            crisis_response=build_crisis_response(decision),
        )
    return MessageCheck(risk="none", categories=[], crisis_response=None)


def create_server(
    retriever_factory: RetrieverFactory,
    *,
    lifespan: Callable[[MCPServer[Any]], Any] | None = None,
) -> MCPServer[Any]:
    """Build the Puente MCP server. ``retriever_factory`` connects the knowledge base."""
    retriever = LazyRetriever(retriever_factory)
    server: MCPServer[Any] = MCPServer(
        name="puente",
        title="Puente: mental health first-barrier tools for Peru",
        instructions=INSTRUCTIONS,
        lifespan=lifespan,
    )

    @server.tool(annotations=READ_ONLY)
    def check_message(text: Text) -> MessageCheck:
        """Check a person's message for crisis signals (suicide, self-harm, violence).

        Deterministic and offline. Call it on every message before answering. When risk is
        "crisis", show crisis_response to the person instead of a normal answer.
        """
        return _check(text)

    @server.tool(annotations=READ_ONLY)
    async def search_guidance(
        query: Text, k: Annotated[int, Field(ge=1, le=MAX_RESULTS)] = 4
    ) -> GuidanceSearch:
        """Search the WHO guide "En tiempos de estrés, haz lo que importa" (Spanish).

        Hybrid search (vectors + Spanish full text) over lay self-help material only. The query
        is checked for crisis first: on a crisis, no search runs and crisis_response is set.
        """
        check = _check(query)
        if check.crisis_response is not None:
            return GuidanceSearch(
                crisis_response=check.crisis_response, results=[], license_note=LICENSE_NOTE
            )
        try:
            chunks = await (await retriever.get()).retrieve(query, k)
        except Exception as exc:
            logger.warning("Guidance search failed (%s).", type(exc).__name__)
            raise ToolError("The knowledge base is unavailable; try again later.") from None
        return GuidanceSearch(
            crisis_response=None,
            results=[
                GuidanceResult(
                    rank=chunk.rank,
                    source_title=chunk.source_title,
                    section_title=chunk.section_title,
                    pages=format_pages(chunk.printed_pages),
                    text=chunk.text,
                    attribution=chunk.attribution,
                    url=chunk.url,
                )
                for chunk in chunks
            ],
            license_note=LICENSE_NOTE,
        )

    @server.tool(annotations=READ_ONLY)
    def crisis_resources() -> CrisisResources:
        """Peru crisis lines (Línea 113 opción 5, SAMU 106, police, Línea 100, firefighters).

        Each resource says whether it has been verified against an official source.
        """
        return CrisisResources(resources=list(CRISIS_RESOURCES), note=COMMUNITY_MENTAL_HEALTH_NOTE)

    return server


def _settings_factory(settings: Settings, pools: list[Any]) -> RetrieverFactory:
    """Connect the knowledge base from settings, like the HTTP API does."""

    async def factory() -> RetrieverPort:
        # Imported here so the guardian tools never depend on the database stack.
        from puente.knowledge.embeddings import FastEmbedEmbedder, model_spec
        from puente.knowledge.retriever import KnowledgeRetriever
        from puente.knowledge.store import PgKnowledgeStore, open_pool

        if settings.database_url is None:
            raise RuntimeError("PUENTE_DATABASE_URL is not set")
        pool = await open_pool(
            settings.database_url.get_secret_value(), timeout=settings.database_connect_timeout
        )
        try:
            spec = model_spec(settings.embedding_model)
            embedder = FastEmbedEmbedder(spec, cache_dir=settings.embedding_cache_dir)
            await embedder.warm_up()
        except BaseException:
            await pool.close()
            raise
        pools.append(pool)
        return KnowledgeRetriever(
            embedder, PgKnowledgeStore(pool, spec), mode=settings.retrieval_mode
        )

    return factory


def main() -> None:
    """Run the server over stdio (``puente-mcp``). Logs go to stderr; stdout is the protocol."""
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    pools: list[Any] = []

    @asynccontextmanager
    async def lifespan(_: MCPServer[Any]) -> AsyncIterator[None]:
        try:
            yield
        finally:
            for pool in pools:
                await pool.close()

    create_server(_settings_factory(settings, pools), lifespan=lifespan).run("stdio")


if __name__ == "__main__":
    main()
