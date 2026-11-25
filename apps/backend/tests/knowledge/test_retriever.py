import pytest

from puente.knowledge.retriever import KnowledgeRetriever

pytestmark = pytest.mark.asyncio


class RecordingStore:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object, str, int]] = []

    async def search(self, text, vector, *, mode, k):
        self.calls.append((text, vector, mode, k))
        return []


@pytest.mark.parametrize("mode", ["dense", "hybrid"])
async def test_vector_modes_embed_the_query_once(hashing_embedder, mode):
    store = RecordingStore()

    await KnowledgeRetriever(hashing_embedder, store, mode=mode).retrieve("me siento solo", k=4)

    assert hashing_embedder.query_calls == ["me siento solo"]
    ((text, vector, called_mode, k),) = store.calls
    assert (text, called_mode, k) == ("me siento solo", mode, 4)
    assert vector == await hashing_embedder.embed_query("me siento solo")


async def test_lexical_mode_never_embeds(hashing_embedder):
    store = RecordingStore()

    await KnowledgeRetriever(hashing_embedder, store, mode="lexical").retrieve("hola", k=2)

    assert hashing_embedder.query_calls == []
    assert store.calls == [("hola", None, "lexical", 2)]
