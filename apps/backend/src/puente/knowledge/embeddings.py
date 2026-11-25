"""Local embedding models: a closed registry and the fastembed (ONNX, CPU) adapter.

Embeddings never go through a third-party API: a query embedding is derived from the user's
message, which is sensitive personal data under Ley 29733.
"""

import asyncio
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

_SLUG = re.compile(r"^[a-z][a-z0-9_]{0,40}$")


@dataclass(frozen=True)
class EmbeddingModelSpec:
    name: str
    """Model id as fastembed knows it."""
    slug: str
    """SQL-safe suffix for the model's embedding table."""
    dim: int
    query_prefix: str = ""
    passage_prefix: str = ""
    """Instruction prefixes the model was trained with (fastembed does not add them)."""

    def __post_init__(self) -> None:
        if not _SLUG.match(self.slug):
            raise ValueError(f"invalid embedding model slug: {self.slug!r}")
        if not 1 <= self.dim <= 2000:
            raise ValueError("pgvector HNSW indexes support at most 2000 dimensions")


KNOWN_MODELS: dict[str, EmbeddingModelSpec] = {
    spec.name: spec
    for spec in (
        EmbeddingModelSpec(
            "intfloat/multilingual-e5-large", "e5_large", 1024, "query: ", "passage: "
        ),
        EmbeddingModelSpec("jinaai/jina-embeddings-v2-base-es", "jina_v2_es", 768),
        EmbeddingModelSpec(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "minilm_l12", 384
        ),
    )
}


def model_spec(name: str) -> EmbeddingModelSpec:
    try:
        return KNOWN_MODELS[name]
    except KeyError:
        known = ", ".join(sorted(KNOWN_MODELS))
        raise ValueError(f"unknown embedding model {name!r}; known: {known}") from None


class FastEmbedEmbedder:
    """fastembed adapter. The model loads lazily on first use and runs in a worker thread."""

    def __init__(
        self,
        spec: EmbeddingModelSpec,
        *,
        cache_dir: str | None = None,
        threads: int | None = None,
        model_factory: Callable[[EmbeddingModelSpec], Any] | None = None,
    ) -> None:
        self.spec = spec
        self._cache_dir = cache_dir
        self._threads = threads
        self._factory = model_factory or self._load
        self._model: Any = None
        self._lock = asyncio.Lock()

    async def _loaded(self) -> Any:
        async with self._lock:
            if self._model is None:
                self._model = await asyncio.to_thread(self._factory, self.spec)
        return self._model

    def _load(self, spec: EmbeddingModelSpec) -> Any:
        from fastembed import TextEmbedding

        return TextEmbedding(spec.name, cache_dir=self._cache_dir, threads=self._threads)

    async def _embed(self, texts: list[str]) -> list[list[float]]:
        model = await self._loaded()
        vectors = await asyncio.to_thread(lambda: list(model.embed(texts)))
        return [[float(value) for value in vector] for vector in vectors]

    async def embed_query(self, text: str) -> list[float]:
        (vector,) = await self._embed([self.spec.query_prefix + text])
        return vector

    async def embed_passages(self, texts: Sequence[str]) -> list[list[float]]:
        return await self._embed([self.spec.passage_prefix + text for text in texts])

    async def warm_up(self) -> None:
        """Load the model ahead of the first request."""
        await self._loaded()
