import numpy as np
import pytest

from puente.knowledge.embeddings import (
    KNOWN_MODELS,
    EmbeddingModelSpec,
    FastEmbedEmbedder,
    model_spec,
)


class RecordingModel:
    def __init__(self) -> None:
        self.embedded: list[list[str]] = []

    def embed(self, texts):
        texts = list(texts)
        self.embedded.append(texts)
        return [np.array([float(len(text)), 1.0]) for text in texts]


def _embedder(spec: EmbeddingModelSpec) -> tuple[FastEmbedEmbedder, RecordingModel, list[int]]:
    model = RecordingModel()
    loads: list[int] = []

    def factory(_spec):
        loads.append(1)
        return model

    return FastEmbedEmbedder(spec, model_factory=factory), model, loads


@pytest.mark.asyncio
async def test_e5_gets_its_query_and_passage_prefixes():
    embedder, model, _ = _embedder(model_spec("intfloat/multilingual-e5-large"))

    await embedder.embed_query("me siento solo")
    await embedder.embed_passages(["Respira lento."])

    assert model.embedded == [["query: me siento solo"], ["passage: Respira lento."]]


@pytest.mark.asyncio
async def test_models_without_prefixes_embed_the_text_as_is():
    embedder, model, _ = _embedder(model_spec("jinaai/jina-embeddings-v2-base-es"))

    vector = await embedder.embed_query("hola")

    assert model.embedded == [["hola"]]
    assert vector == [4.0, 1.0]


@pytest.mark.asyncio
async def test_model_loads_once():
    embedder, _, loads = _embedder(model_spec("jinaai/jina-embeddings-v2-base-es"))

    await embedder.warm_up()
    await embedder.embed_query("uno")
    await embedder.embed_passages(["dos", "tres"])

    assert loads == [1]


def test_model_spec_rejects_unknown_models():
    with pytest.raises(ValueError, match="unknown embedding model"):
        model_spec("openai/text-embedding-3-large")


def test_registry_slugs_are_unique_and_dimensions_fit_hnsw():
    slugs = [spec.slug for spec in KNOWN_MODELS.values()]

    assert len(slugs) == len(set(slugs))
    assert all(spec.dim <= 2000 for spec in KNOWN_MODELS.values())


@pytest.mark.parametrize("slug", ["Bad-Slug", "1abc", "x; drop table"])
def test_spec_rejects_unsafe_slugs(slug):
    with pytest.raises(ValueError, match="invalid embedding model slug"):
        EmbeddingModelSpec("some/model", slug, 8)
