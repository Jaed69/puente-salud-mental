"""Shared fakes and fixtures for the knowledge tests.

Integration tests need PostgreSQL with pgvector. They run only when ``PUENTE_TEST_DATABASE_URL`` is
set (for example ``postgresql://puente:puente-dev@127.0.0.1:5433/puente``); each test gets its own
schema, dropped afterwards.
"""

import hashlib
import math
import os
import re
import uuid
from collections.abc import AsyncIterator, Sequence

import pytest
import pytest_asyncio

from puente.knowledge.corpus import Chunk
from puente.knowledge.embeddings import EmbeddingModelSpec

TEST_DATABASE_URL = os.environ.get("PUENTE_TEST_DATABASE_URL")

FAKE_MODEL = EmbeddingModelSpec(name="test/hashing", slug="test_hashing", dim=64)

_WORD = re.compile(r"\w+")


class HashingEmbedder:
    """Deterministic bag-of-words embedder: texts sharing words get similar vectors."""

    def __init__(self, spec: EmbeddingModelSpec = FAKE_MODEL) -> None:
        self.spec = spec
        self.query_calls: list[str] = []

    def _vector(self, text: str) -> list[float]:
        vector = [0.0] * self.spec.dim
        for word in _WORD.findall(text.casefold()):
            digest = hashlib.sha256(word.encode()).digest()
            vector[digest[0] % self.spec.dim] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    async def embed_query(self, text: str) -> list[float]:
        self.query_calls.append(text)
        return self._vector(text)

    async def embed_passages(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]


def make_chunk(
    chunk_id: str,
    text: str,
    *,
    source_id: str = "test-book",
    audience: str = "lay",
    content_type: str = "exercise",
    pages: tuple[int, ...] = (1,),
) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        source_id=source_id,
        source_title="Libro de prueba",
        section_id="p1",
        section_title="Parte 1",
        pdf_pages=pages,
        printed_pages=pages,
        text=text,
        embedding_text=f"Libro de prueba — Parte 1\n{text}",
        audience=audience,  # type: ignore[arg-type]
        content_type=content_type,  # type: ignore[arg-type]
        licence="CC BY-NC-SA 3.0 IGO",
        attribution="Libro de prueba. Licencia: CC BY-NC-SA 3.0 IGO.",
        url="https://example.org/book.pdf",
    )


@pytest.fixture
def hashing_embedder() -> HashingEmbedder:
    return HashingEmbedder()


@pytest_asyncio.fixture
async def database_url() -> AsyncIterator[str]:
    """A connection string whose search path is a fresh, throwaway schema."""
    if not TEST_DATABASE_URL:
        pytest.skip("PUENTE_TEST_DATABASE_URL is not set")
    import psycopg

    schema = f"test_{uuid.uuid4().hex[:12]}"
    async with await psycopg.AsyncConnection.connect(TEST_DATABASE_URL, autocommit=True) as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.execute(f'CREATE SCHEMA "{schema}"')
    separator = "&" if "?" in TEST_DATABASE_URL else "?"
    try:
        yield f"{TEST_DATABASE_URL}{separator}options=-csearch_path%3D{schema},public"
    finally:
        async with await psycopg.AsyncConnection.connect(
            TEST_DATABASE_URL, autocommit=True
        ) as conn:
            await conn.execute(f'DROP SCHEMA "{schema}" CASCADE')
