"""PostgreSQL + pgvector knowledge store: chunks, per-model embeddings and three search modes.

- ``knowledge_chunk`` holds the text and metadata, with a generated Spanish ``tsvector``.
- ``knowledge_embedding_<slug>`` holds one embedding model's vectors with an HNSW cosine index, so
  several models can be indexed side by side for evaluation.
- Search: ``dense`` (cosine), ``lexical`` (full-text, any word, Spanish stemming) or ``hybrid``
  (Reciprocal Rank Fusion of both). Every mode serves lay material only.

Table names come from the closed model registry (``EmbeddingModelSpec.slug``), never from input.
"""

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass

from psycopg import AsyncConnection, sql
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from puente.knowledge.corpus import Chunk
from puente.knowledge.embeddings import EmbeddingModelSpec
from puente.knowledge.ports import EmbedderPort, RetrievalMode, RetrievedChunk

RRF_K = 60
"""Reciprocal Rank Fusion constant from Cormack et al. (2009)."""
CANDIDATE_POOL = 50
"""Candidates each ranker contributes before fusion."""
EXCLUDED_CONTENT_TYPES = ["dosing", "diagnostic"]
EMBED_BATCH = 16

_CHUNK_TABLE = """
CREATE TABLE IF NOT EXISTS knowledge_chunk (
    chunk_id       text PRIMARY KEY,
    source_id      text NOT NULL,
    source_title   text NOT NULL,
    section_id     text NOT NULL,
    section_title  text NOT NULL,
    printed_pages  integer[] NOT NULL,
    text           text NOT NULL,
    embedding_text text NOT NULL,
    audience       text NOT NULL CHECK (audience IN ('lay', 'clinician', 'helper')),
    content_type   text NOT NULL,
    licence        text NOT NULL,
    attribution    text NOT NULL,
    url            text NOT NULL,
    content_hash   text NOT NULL,
    tsv            tsvector GENERATED ALWAYS AS (to_tsvector('spanish', embedding_text)) STORED
);
CREATE INDEX IF NOT EXISTS knowledge_chunk_tsv_idx ON knowledge_chunk USING gin (tsv);
CREATE INDEX IF NOT EXISTS knowledge_chunk_source_idx ON knowledge_chunk (source_id);
"""

_EMBEDDING_TABLE = """
CREATE TABLE IF NOT EXISTS {table} (
    chunk_id     text PRIMARY KEY REFERENCES knowledge_chunk (chunk_id) ON DELETE CASCADE,
    content_hash text NOT NULL,
    embedding    vector({dim}) NOT NULL
);
CREATE INDEX IF NOT EXISTS {index} ON {table} USING hnsw (embedding vector_cosine_ops);
"""

_LAY_FILTER = "c.audience = 'lay' AND c.content_type <> ALL(%(excluded)s)"

# Any-word Spanish query: plainto_tsquery ANDs the stems; turning '&' into '|' makes it OR. The
# result is cast with ::tsquery, not to_tsquery(), which would stem the stems a second time.
_LEXICAL_QUERY = "replace(plainto_tsquery('spanish', %(text)s)::text, '&', '|')::tsquery"

_DENSE_CTE = f"""
dense AS (
    SELECT c.chunk_id, row_number() OVER (ORDER BY e.embedding <=> %(vector)s::vector) AS rank
    FROM {{table}} e JOIN knowledge_chunk c USING (chunk_id)
    WHERE {_LAY_FILTER}
    ORDER BY e.embedding <=> %(vector)s::vector
    LIMIT %(pool)s
)"""

_LEXICAL_CTE = f"""
lexical AS (
    SELECT c.chunk_id, row_number() OVER (ORDER BY ts_rank_cd(c.tsv, q) DESC, c.chunk_id) AS rank
    FROM knowledge_chunk c CROSS JOIN (SELECT {_LEXICAL_QUERY} AS q) lexical_query
    WHERE c.tsv @@ q AND {_LAY_FILTER}
    ORDER BY ts_rank_cd(c.tsv, q) DESC, c.chunk_id
    LIMIT %(pool)s
)"""

_SELECT_RANKED = """
SELECT c.chunk_id, c.source_id, c.source_title, c.section_title, c.printed_pages, c.text,
       c.attribution, c.url, ranked.score
FROM ranked JOIN knowledge_chunk c USING (chunk_id)
ORDER BY ranked.score DESC, c.chunk_id
LIMIT %(k)s
"""

_RANKED = {
    "dense": "ranked AS (SELECT chunk_id, 1.0 / (%(rrf_k)s + rank) AS score FROM dense)",
    "lexical": "ranked AS (SELECT chunk_id, 1.0 / (%(rrf_k)s + rank) AS score FROM lexical)",
    "hybrid": """ranked AS (
        SELECT chunk_id, sum(1.0 / (%(rrf_k)s + rank)) AS score
        FROM (SELECT * FROM dense UNION ALL SELECT * FROM lexical) fused
        GROUP BY chunk_id
    )""",
}


@dataclass(frozen=True)
class IngestReport:
    upserted: int
    removed: int
    embedded: int


async def open_pool(conninfo: str, *, max_size: int = 5) -> AsyncConnectionPool:
    async def configure(conn: AsyncConnection) -> None:
        from pgvector.psycopg import register_vector_async

        await register_vector_async(conn)

    # The extension must exist before the vector type can be registered on pooled connections.
    async with await AsyncConnection.connect(conninfo, autocommit=True) as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    pool = AsyncConnectionPool(
        conninfo, min_size=1, max_size=max_size, configure=configure, open=False
    )
    await pool.open(wait=True)
    return pool


class PgKnowledgeStore:
    def __init__(self, pool: AsyncConnectionPool, model: EmbeddingModelSpec) -> None:
        self._pool = pool
        self.model = model
        self._table = sql.Identifier(f"knowledge_embedding_{model.slug}")

    async def ensure_schema(self) -> None:
        embedding_ddl = sql.SQL(_EMBEDDING_TABLE).format(
            table=self._table,
            index=sql.Identifier(f"knowledge_embedding_{self.model.slug}_hnsw"),
            dim=sql.Literal(self.model.dim),
        )
        async with self._pool.connection() as conn:
            await conn.execute(_CHUNK_TABLE)
            await conn.execute(embedding_ddl)

    async def replace_source(self, source_id: str, chunks: Sequence[Chunk]) -> tuple[int, int]:
        """Upsert the source's chunks and delete the ones it no longer has."""
        if any(chunk.source_id != source_id for chunk in chunks):
            raise ValueError("every chunk must belong to the source being replaced")
        rows = [_chunk_row(chunk) for chunk in chunks]
        async with self._pool.connection() as conn, conn.cursor() as cur:
            await cur.executemany(
                """
                INSERT INTO knowledge_chunk (chunk_id, source_id, source_title, section_id,
                    section_title, printed_pages, text, embedding_text, audience, content_type,
                    licence, attribution, url, content_hash)
                VALUES (%(chunk_id)s, %(source_id)s, %(source_title)s, %(section_id)s,
                    %(section_title)s, %(printed_pages)s, %(text)s, %(embedding_text)s,
                    %(audience)s, %(content_type)s, %(licence)s, %(attribution)s, %(url)s,
                    %(content_hash)s)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    source_id = EXCLUDED.source_id, source_title = EXCLUDED.source_title,
                    section_id = EXCLUDED.section_id, section_title = EXCLUDED.section_title,
                    printed_pages = EXCLUDED.printed_pages, text = EXCLUDED.text,
                    embedding_text = EXCLUDED.embedding_text, audience = EXCLUDED.audience,
                    content_type = EXCLUDED.content_type, licence = EXCLUDED.licence,
                    attribution = EXCLUDED.attribution, url = EXCLUDED.url,
                    content_hash = EXCLUDED.content_hash
                """,
                rows,
            )
            await cur.execute(
                "DELETE FROM knowledge_chunk WHERE source_id = %s AND NOT chunk_id = ANY(%s)",
                (source_id, [row["chunk_id"] for row in rows]),
            )
            removed = cur.rowcount
        return len(rows), removed

    async def stale_embeddings(self) -> list[tuple[str, str, str]]:
        """(chunk_id, embedding_text, content_hash) of chunks whose vector is missing or stale."""
        query = sql.SQL(
            """
            SELECT c.chunk_id, c.embedding_text, c.content_hash
            FROM knowledge_chunk c LEFT JOIN {table} e USING (chunk_id)
            WHERE e.chunk_id IS NULL OR e.content_hash <> c.content_hash
            ORDER BY c.chunk_id
            """
        ).format(table=self._table)
        async with self._pool.connection() as conn:
            cur = await conn.execute(query)
            return [tuple(row) for row in await cur.fetchall()]

    async def upsert_embeddings(self, items: Sequence[tuple[str, str, list[float]]]) -> None:
        query = sql.SQL(
            """
            INSERT INTO {table} (chunk_id, content_hash, embedding)
            VALUES (%s, %s, %s::vector)
            ON CONFLICT (chunk_id) DO UPDATE SET
                content_hash = EXCLUDED.content_hash, embedding = EXCLUDED.embedding
            """
        ).format(table=self._table)
        async with self._pool.connection() as conn, conn.cursor() as cur:
            await cur.executemany(query, [(cid, h, str(vector)) for cid, h, vector in items])

    async def search(
        self, text: str, vector: Sequence[float] | None, *, mode: RetrievalMode, k: int
    ) -> list[RetrievedChunk]:
        if mode not in _RANKED:
            raise ValueError(f"unknown retrieval mode: {mode!r}")
        if mode != "lexical" and vector is None:
            raise ValueError(f"{mode} search needs a query vector")
        ctes = {
            "dense": [_DENSE_CTE],
            "lexical": [_LEXICAL_CTE],
            "hybrid": [_DENSE_CTE, _LEXICAL_CTE],
        }[mode]
        query = sql.SQL("WITH " + ",".join([*ctes, _RANKED[mode]]) + _SELECT_RANKED).format(
            table=self._table
        )
        params = {
            "text": text,
            "vector": str(list(vector)) if vector is not None else None,
            "pool": CANDIDATE_POOL,
            "rrf_k": RRF_K,
            "k": k,
            "excluded": EXCLUDED_CONTENT_TYPES,
        }
        async with self._pool.connection() as conn, conn.transaction():
            # HNSW returns at most ef_search rows; keep it above the candidate pool.
            await conn.execute(f"SET LOCAL hnsw.ef_search = {max(CANDIDATE_POOL * 2, 100)}")
            cur = conn.cursor(row_factory=dict_row)
            await cur.execute(query, params)
            rows = await cur.fetchall()
        return [
            RetrievedChunk(
                chunk_id=row["chunk_id"],
                source_id=row["source_id"],
                source_title=row["source_title"],
                section_title=row["section_title"],
                printed_pages=tuple(row["printed_pages"]),
                text=row["text"],
                attribution=row["attribution"],
                url=row["url"],
                score=float(row["score"]),
                rank=rank,
            )
            for rank, row in enumerate(rows, start=1)
        ]


async def ingest(
    store: PgKnowledgeStore, embedder: EmbedderPort, source_id: str, chunks: Sequence[Chunk]
) -> IngestReport:
    """Replace a source's chunks, then embed only the chunks whose text changed."""
    upserted, removed = await store.replace_source(source_id, chunks)
    stale = await store.stale_embeddings()
    for start in range(0, len(stale), EMBED_BATCH):
        batch = stale[start : start + EMBED_BATCH]
        vectors = await embedder.embed_passages([text for _, text, _ in batch])
        await store.upsert_embeddings(
            [(cid, h, vector) for (cid, _, h), vector in zip(batch, vectors, strict=True)]
        )
    return IngestReport(upserted=upserted, removed=removed, embedded=len(stale))


def _chunk_row(chunk: Chunk) -> dict[str, object]:
    return {
        "chunk_id": chunk.chunk_id,
        "source_id": chunk.source_id,
        "source_title": chunk.source_title,
        "section_id": chunk.section_id,
        "section_title": chunk.section_title,
        "printed_pages": list(chunk.printed_pages),
        "text": chunk.text,
        "embedding_text": chunk.embedding_text,
        "audience": chunk.audience,
        "content_type": chunk.content_type,
        "licence": chunk.licence,
        "attribution": chunk.attribution,
        "url": chunk.url,
        "content_hash": hashlib.sha256(chunk.embedding_text.encode()).hexdigest(),
    }
