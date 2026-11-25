"""Retriever: embeds the query locally when the mode needs it and searches the store."""

from collections.abc import Sequence
from typing import Protocol

from puente.knowledge.ports import EmbedderPort, RetrievalMode, RetrievedChunk


class SearchableStore(Protocol):
    async def search(
        self, text: str, vector: Sequence[float] | None, *, mode: RetrievalMode, k: int
    ) -> list[RetrievedChunk]: ...


class KnowledgeRetriever:
    def __init__(
        self, embedder: EmbedderPort, store: SearchableStore, *, mode: RetrievalMode = "hybrid"
    ) -> None:
        self._embedder = embedder
        self._store = store
        self.mode = mode

    async def retrieve(self, query: str, k: int) -> list[RetrievedChunk]:
        vector = None if self.mode == "lexical" else await self._embedder.embed_query(query)
        return await self._store.search(query, vector, mode=self.mode, k=k)
