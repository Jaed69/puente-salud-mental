"""Integration tests for the pgvector store (skipped without PUENTE_TEST_DATABASE_URL)."""

import pytest
from conftest import FAKE_MODEL, make_chunk

from puente.knowledge.store import PgKnowledgeStore, ingest, open_pool

pytestmark = pytest.mark.asyncio

BREATHING = make_chunk("b:p1:001-001", "Respira lento y presiona los pies contra el suelo.")
VALUES = make_chunk(
    "b:p3:010-010", "Elige tus valores y da un pequeño paso hacia ellos.", pages=(10,)
)
KINDNESS = make_chunk("b:p4:020-020", "Háblate con amabilidad cuando sufres.", pages=(20,))
CLINICAL = make_chunk(
    "b:x:030-030",
    "Respira lento: dosis de sertralina.",
    audience="clinician",
    content_type="dosing",
)


async def _store(database_url, embedder, chunks=(BREATHING, VALUES, KINDNESS)):
    pool = await open_pool(database_url)
    store = PgKnowledgeStore(pool, FAKE_MODEL)
    await store.ensure_schema()
    await ingest(store, embedder, "test-book", chunks)
    return pool, store


async def test_ingest_reports_upserts_and_embeds_only_changed_chunks(
    database_url, hashing_embedder
):
    pool = await open_pool(database_url)
    try:
        store = PgKnowledgeStore(pool, FAKE_MODEL)
        await store.ensure_schema()
        await store.ensure_schema()  # idempotent

        first = await ingest(store, hashing_embedder, "test-book", (BREATHING, VALUES))
        second = await ingest(store, hashing_embedder, "test-book", (BREATHING, VALUES))

        assert (first.upserted, first.removed, first.embedded) == (2, 0, 2)
        assert (second.upserted, second.removed, second.embedded) == (2, 0, 0)
    finally:
        await pool.close()


async def test_reingest_removes_chunks_no_longer_in_the_source(database_url, hashing_embedder):
    pool, store = await _store(database_url, hashing_embedder)
    try:
        report = await ingest(store, hashing_embedder, "test-book", (BREATHING,))
        results = await store.search("valores", None, mode="lexical", k=5)

        assert report.removed == 2
        assert results == []
    finally:
        await pool.close()


@pytest.mark.parametrize("mode", ["dense", "lexical", "hybrid"])
async def test_search_ranks_the_matching_chunk_first(database_url, hashing_embedder, mode):
    pool, store = await _store(database_url, hashing_embedder)
    try:
        query = "elige tus valores"
        vector = await hashing_embedder.embed_query(query) if mode != "lexical" else None

        results = await store.search(query, vector, mode=mode, k=3)

        assert results[0].chunk_id == VALUES.chunk_id
        assert results[0].rank == 1
        assert results[0].printed_pages == (10,)
        assert results[0].attribution.endswith("CC BY-NC-SA 3.0 IGO.")
        assert [r.score for r in results] == sorted((r.score for r in results), reverse=True)
    finally:
        await pool.close()


async def test_lexical_search_matches_any_word_and_spanish_stems(database_url, hashing_embedder):
    pool, store = await _store(database_url, hashing_embedder)
    try:
        # "respirando" stems like "respira"; "nadie" appears in no chunk and must not block it.
        results = await store.search("respirando nadie", None, mode="lexical", k=3)

        assert [r.chunk_id for r in results] == [BREATHING.chunk_id]
    finally:
        await pool.close()


@pytest.mark.parametrize("mode", ["dense", "lexical", "hybrid"])
async def test_search_never_returns_clinician_or_dosing_material(
    database_url, hashing_embedder, mode
):
    pool, store = await _store(database_url, hashing_embedder, (BREATHING, CLINICAL))
    try:
        query = "respira lento dosis"
        vector = await hashing_embedder.embed_query(query) if mode != "lexical" else None

        results = await store.search(query, vector, mode=mode, k=5)

        assert [r.chunk_id for r in results] == [BREATHING.chunk_id]
    finally:
        await pool.close()


async def test_search_requires_a_vector_for_dense_and_hybrid(database_url, hashing_embedder):
    pool, store = await _store(database_url, hashing_embedder)
    try:
        with pytest.raises(ValueError, match="query vector"):
            await store.search("valores", None, mode="hybrid", k=3)
    finally:
        await pool.close()
