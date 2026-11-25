"""Grounded replies: retrieval runs between the input guardian and the companion."""

import asyncio
import logging

from fastapi.testclient import TestClient

from puente.api.messages import COMPANION_FALLBACK, get_chat_model, get_retriever
from puente.config import Settings
from puente.knowledge.ports import RetrievedChunk
from puente.main import create_app

QUERY = "últimamente me hablo muy feo a mí misma"

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
BREATH = RetrievedChunk(
    **{**KIND.__dict__, "chunk_id": "who-dwm-2020-es:h1:122-122", "printed_pages": (122,)}
)


class FakeChatModel:
    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.calls: list[list[dict[str, str]]] = []

    async def complete(self, messages):
        self.calls.append(list(messages))
        return self.reply


class FakeRetriever:
    def __init__(self, chunks=(KIND, BREATH), error: Exception | None = None, delay: float = 0):
        self.chunks = list(chunks)
        self.error = error
        self.delay = delay
        self.queries: list[tuple[str, int]] = []

    async def retrieve(self, query: str, k: int):
        self.queries.append((query, k))
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error is not None:
            raise self.error
        return self.chunks[:k]


def _client(model, retriever, **settings) -> TestClient:
    app = create_app(Settings(_env_file=None, environment="test", **settings))
    app.dependency_overrides[get_chat_model] = lambda: model
    app.dependency_overrides[get_retriever] = lambda: retriever
    return TestClient(app)


def test_cited_reply_returns_clean_text_and_its_sources():
    model = FakeChatModel("Intenta hablarte como a una amiga [1].")
    retriever = FakeRetriever()

    response = _client(model, retriever, retrieval_k=3).post("/v1/messages", json={"text": QUERY})

    assert response.status_code == 200
    assert response.json() == {
        "type": "reply",
        "message": "Intenta hablarte como a una amiga.",
        "sources": [
            {
                "source_title": KIND.source_title,
                "section_title": "Parte 4: Ser amable",
                "pages": "100-102",
                "attribution": KIND.attribution,
                "url": KIND.url,
            }
        ],
    }
    assert retriever.queries == [(QUERY, 3)]


def test_retrieved_material_reaches_the_model_as_numbered_references():
    model = FakeChatModel("Te escucho.")

    _client(model, FakeRetriever()).post("/v1/messages", json={"text": QUERY})

    (messages,) = model.calls
    system = messages[0]["content"]
    assert messages[0]["role"] == "system"
    assert "[1] Parte 4: Ser amable, págs. 100-102" in system
    assert KIND.text in system
    assert messages[-1] == {"role": "user", "content": QUERY}


def test_uncited_reply_keeps_the_previous_response_shape():
    model = FakeChatModel("Te escucho. ¿Qué pasó hoy?")

    response = _client(model, FakeRetriever()).post("/v1/messages", json={"text": QUERY})

    assert response.json() == {"type": "reply", "message": "Te escucho. ¿Qué pasó hoy?"}


def test_citation_of_a_chunk_that_was_not_retrieved_is_dropped():
    model = FakeChatModel("Esto lo inventé [7].")

    response = _client(model, FakeRetriever()).post("/v1/messages", json={"text": QUERY})

    assert response.json() == {"type": "reply", "message": "Esto lo inventé."}


def test_crisis_message_never_reaches_retrieval():
    model = FakeChatModel("no debería llamarse")
    retriever = FakeRetriever()

    response = _client(model, retriever).post("/v1/messages", json={"text": "ya no quiero vivir"})

    assert response.json()["type"] == "crisis"
    assert retriever.queries == []
    assert model.calls == []


def test_unconfigured_model_skips_retrieval_and_serves_fallback():
    retriever = FakeRetriever()

    response = _client(None, retriever).post("/v1/messages", json={"text": QUERY})

    assert response.json() == {"type": "reply", "message": COMPANION_FALLBACK}
    assert retriever.queries == []


def test_retrieval_failure_degrades_to_an_ungrounded_reply_without_logging_text(caplog):
    model = FakeChatModel("Te escucho.")
    retriever = FakeRetriever(error=ConnectionError(QUERY))

    with caplog.at_level(logging.DEBUG):
        response = _client(model, retriever).post("/v1/messages", json={"text": QUERY})

    assert response.json() == {"type": "reply", "message": "Te escucho."}
    assert "[1]" not in model.calls[0][0]["content"]
    assert "ConnectionError" in caplog.text
    assert QUERY not in caplog.text


def test_slow_retrieval_times_out_to_an_ungrounded_reply():
    model = FakeChatModel("Te escucho.")
    retriever = FakeRetriever(delay=5)

    response = _client(model, retriever, retrieval_timeout_seconds=0.05).post(
        "/v1/messages", json={"text": QUERY}
    )

    assert response.json() == {"type": "reply", "message": "Te escucho."}


def test_grounded_reply_that_trips_the_lexicon_returns_crisis_response():
    model = FakeChatModel("A veces pienso en suicidarme también [1].")

    response = _client(model, FakeRetriever()).post("/v1/messages", json={"text": QUERY})

    body = response.json()
    assert body["type"] == "crisis"
    assert "sources" not in body


def test_app_without_a_retriever_answers_as_before():
    model = FakeChatModel("Te escucho [1].")

    response = _client(model, None).post("/v1/messages", json={"text": QUERY})

    assert response.json() == {"type": "reply", "message": "Te escucho."}
