"""The MCP server: tools for any model to use Puente's guardian and knowledge base."""

import logging

import pytest
from mcp import Client

from puente.knowledge.ports import RetrievedChunk
from puente.mcp_server import create_server

pytestmark = pytest.mark.asyncio

KIND = RetrievedChunk(
    chunk_id="who-dwm-2020-es:p4:100-102",
    source_id="who-dwm-2020-es",
    source_title="En tiempos de estrés, haz lo que importa: una guía ilustrada",
    section_title="Parte 4: Ser amable",
    printed_pages=(100, 101, 102),
    text="Háblate a ti misma con amabilidad, como le hablarías a una amiga.",
    attribution="OMS; 2020. Licencia: CC BY-NC-SA 3.0 IGO.",
    url="https://www.who.int/docs/default-source/mental-health/sh-2020-spa-3-web.pdf",
    score=0.032,
    rank=1,
)


class FakeRetriever:
    def __init__(self, chunks=(KIND,)):
        self.chunks = list(chunks)
        self.calls: list[tuple[str, int]] = []

    async def retrieve(self, query: str, k: int) -> list[RetrievedChunk]:
        self.calls.append((query, k))
        return self.chunks[:k]


def factory_for(retriever):
    calls = []

    async def factory():
        calls.append(1)
        return retriever

    factory.calls = calls
    return factory


async def failing_factory():
    raise ConnectionError("db down")


async def call(server, tool, args):
    async with Client(server) as client:
        return await client.call_tool(tool, args)


async def test_lists_the_three_read_only_tools():
    async with Client(create_server(factory_for(FakeRetriever()))) as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}

    assert set(tools) == {"check_message", "search_guidance", "crisis_resources"}
    assert all(tool.annotations and tool.annotations.read_only_hint for tool in tools.values())


async def test_check_message_without_risk():
    result = await call(
        create_server(factory_for(FakeRetriever())),
        "check_message",
        {"text": "hoy fue un día largo"},
    )

    assert not result.is_error
    assert result.structured_content == {"risk": "none", "categories": [], "crisis_response": None}


async def test_check_message_returns_the_fixed_crisis_response():
    result = await call(
        create_server(factory_for(FakeRetriever())), "check_message", {"text": "ya no quiero vivir"}
    )

    content = result.structured_content
    assert content["risk"] == "crisis"
    assert "suicidal_ideation" in content["categories"]
    assert "Línea 113, opción 5" in content["crisis_response"]["message"]
    assert content["crisis_response"]["resources"][0]["id"] == "minsa_113_5"


async def test_search_guidance_returns_cited_lay_material():
    retriever = FakeRetriever()
    result = await call(
        create_server(factory_for(retriever)),
        "search_guidance",
        {"query": "me hablo muy feo", "k": 3},
    )

    content = result.structured_content
    assert retriever.calls == [("me hablo muy feo", 3)]
    assert content["crisis_response"] is None
    assert content["results"] == [
        {
            "rank": 1,
            "source_title": KIND.source_title,
            "section_title": "Parte 4: Ser amable",
            "pages": "100-102",
            "text": KIND.text,
            "attribution": KIND.attribution,
            "url": KIND.url,
        }
    ]
    assert "CC BY-NC-SA" in content["license_note"]


async def test_search_guidance_checks_for_crisis_before_retrieving():
    factory = factory_for(FakeRetriever())
    result = await call(create_server(factory), "search_guidance", {"query": "quiero matarme"})

    content = result.structured_content
    assert content["results"] == []
    assert "Línea 113" in content["crisis_response"]["message"]
    assert factory.calls == []


@pytest.mark.parametrize(
    "args",
    [{"query": ""}, {"query": "x" * 4001}, {"query": "hola", "k": 0}, {"query": "hola", "k": 11}],
)
async def test_search_guidance_rejects_out_of_range_input(args):
    retriever = FakeRetriever()
    result = await call(create_server(factory_for(retriever)), "search_guidance", args)

    assert result.is_error
    assert retriever.calls == []


async def test_search_guidance_reports_an_unavailable_knowledge_base(caplog):
    caplog.set_level(logging.DEBUG)
    result = await call(
        create_server(failing_factory), "search_guidance", {"query": "me siento cansada"}
    )

    assert result.is_error
    assert "knowledge base is unavailable" in result.content[0].text
    assert "me siento cansada" not in caplog.text


async def test_the_retriever_is_connected_once_and_reused():
    factory = factory_for(FakeRetriever())
    server = create_server(factory)
    async with Client(server) as client:
        await client.call_tool("search_guidance", {"query": "estrés"})
        await client.call_tool("search_guidance", {"query": "valores"})

    assert factory.calls == [1]


async def test_a_failed_connection_is_retried_on_the_next_search():
    attempts = []

    async def flaky():
        attempts.append(1)
        if len(attempts) == 1:
            raise ConnectionError("not yet")
        return FakeRetriever()

    async with Client(create_server(flaky, retry_after_seconds=0.0)) as client:
        first = await client.call_tool("search_guidance", {"query": "estrés"})
        second = await client.call_tool("search_guidance", {"query": "estrés"})

    assert first.is_error
    assert not second.is_error
    assert len(attempts) == 2


async def test_crisis_resources_marks_which_lines_are_verified():
    result = await call(create_server(factory_for(FakeRetriever())), "crisis_resources", {})

    content = result.structured_content
    verified = {r["id"]: r["verified"] for r in content["resources"]}
    assert verified["minsa_113_5"] is True
    assert verified["samu_106"] is False
    assert content["note"]["source"]


async def test_server_instructions_tell_the_model_to_check_every_message():
    async with Client(create_server(factory_for(FakeRetriever()))) as client:
        instructions = client.instructions

    assert "check_message" in instructions
    assert "every" in instructions


async def test_check_message_assesses_long_messages_instead_of_rejecting_them():
    text = "hoy fue un día muy pesado en el trabajo. " * 150 + "ya no quiero vivir"
    assert len(text) > 4000

    result = await call(
        create_server(factory_for(FakeRetriever())), "check_message", {"text": text}
    )

    assert not result.is_error
    assert result.structured_content["risk"] == "crisis"


async def test_after_a_failure_searches_fail_fast_until_the_cooldown_ends():
    attempts = []
    now = [100.0]

    async def failing():
        attempts.append(1)
        raise ConnectionError("db down")

    server = create_server(failing, retry_after_seconds=30.0, clock=lambda: now[0])
    async with Client(server) as client:
        first = await client.call_tool("search_guidance", {"query": "estrés"})
        second = await client.call_tool("search_guidance", {"query": "estrés"})
        now[0] += 31.0
        third = await client.call_tool("search_guidance", {"query": "estrés"})

    assert first.is_error and second.is_error and third.is_error
    assert len(attempts) == 2


async def test_a_missing_database_url_is_reported_as_configuration():
    from puente.config import Settings
    from puente.mcp_server import settings_factory

    server = create_server(settings_factory(Settings(_env_file=None), []))
    result = await call(server, "search_guidance", {"query": "estrés"})

    assert result.is_error
    assert "PUENTE_DATABASE_URL" in result.content[0].text


async def test_settings_factory_closes_the_pool_when_the_embedder_fails(monkeypatch):
    from puente.config import Settings
    from puente.knowledge import embeddings, store
    from puente.mcp_server import settings_factory

    class FakePool:
        closed = False

        async def close(self):
            self.closed = True

    pool = FakePool()

    async def fake_open_pool(conninfo, *, timeout):
        return pool

    class FailingEmbedder:
        def __init__(self, spec, *, cache_dir):
            pass

        async def warm_up(self):
            raise OSError("model download failed")

    monkeypatch.setattr(store, "open_pool", fake_open_pool)
    monkeypatch.setattr(embeddings, "FastEmbedEmbedder", FailingEmbedder)
    pools = []
    factory = settings_factory(Settings(_env_file=None, database_url="postgresql://x@h/db"), pools)

    with pytest.raises(OSError):
        await factory()

    assert pool.closed
    assert pools == []


async def test_settings_factory_keeps_the_pool_on_success(monkeypatch):
    from puente.config import Settings
    from puente.knowledge import embeddings, store
    from puente.knowledge.retriever import KnowledgeRetriever
    from puente.mcp_server import settings_factory

    pool = object()

    async def fake_open_pool(conninfo, *, timeout):
        return pool

    class StubEmbedder:
        def __init__(self, spec, *, cache_dir):
            pass

        async def warm_up(self):
            return None

    monkeypatch.setattr(store, "open_pool", fake_open_pool)
    monkeypatch.setattr(embeddings, "FastEmbedEmbedder", StubEmbedder)
    pools = []
    factory = settings_factory(Settings(_env_file=None, database_url="postgresql://x@h/db"), pools)

    assert isinstance(await factory(), KnowledgeRetriever)
    assert pools == [pool]
