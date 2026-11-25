"""Knowledge ports: what retrieval needs from an embedder and offers to the companion (no I/O)."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol

RetrievalMode = Literal["dense", "lexical", "hybrid"]
RETRIEVAL_MODES: tuple[RetrievalMode, ...] = ("dense", "lexical", "hybrid")


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    source_id: str
    source_title: str
    section_title: str
    printed_pages: tuple[int, ...]
    text: str
    attribution: str
    url: str
    score: float
    rank: int


class EmbedderPort(Protocol):
    async def embed_query(self, text: str) -> list[float]:
        """Embed a user query. Implementations must run locally: queries are sensitive data."""
        ...

    async def embed_passages(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed corpus passages for indexing."""
        ...


class RetrieverPort(Protocol):
    async def retrieve(self, query: str, k: int) -> list[RetrievedChunk]:
        """Return up to ``k`` lay chunks relevant to ``query``, best first."""
        ...
