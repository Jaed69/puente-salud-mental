"""Command line for the knowledge base: ``puente-knowledge fetch|build|ingest|eval``.

Run from ``apps/backend``. Paths default to the committed ``corpus/`` layout. ``ingest`` loads the
committed chunks into PostgreSQL (``PUENTE_DATABASE_URL``) and embeds them locally. ``eval`` scores
every indexed model and retrieval mode on ``eval/retrieval_questions.jsonl`` and writes a report.
"""

import argparse
import asyncio
import statistics
import sys
import time
from collections.abc import Sequence
from datetime import date
from pathlib import Path

import httpx

from puente.config import get_settings
from puente.knowledge.corpus import (
    DWM_SOURCE,
    SourceDocument,
    build_chunks,
    load_chunks,
    read_pdf_pages,
    verify_sha256,
    write_chunks,
)
from puente.knowledge.embeddings import KNOWN_MODELS, FastEmbedEmbedder, model_spec
from puente.knowledge.evaluation import (
    DEFAULT_KS,
    Summary,
    load_questions,
    relevant_chunk_ids,
    render_report,
    score_ranking,
    summarize,
)
from puente.knowledge.retriever import KnowledgeRetriever
from puente.knowledge.store import PgKnowledgeStore, ingest, open_pool

SOURCES: dict[str, SourceDocument] = {DWM_SOURCE.source_id: DWM_SOURCE}
CORPUS_DIR = Path("corpus")
QUESTIONS_PATH = Path("eval/retrieval_questions.jsonl")
REPORTS_DIR = Path("eval/reports")


def raw_path(source: SourceDocument, corpus_dir: Path = CORPUS_DIR) -> Path:
    return corpus_dir / "raw" / f"{source.source_id}.pdf"


def chunks_path(source: SourceDocument, corpus_dir: Path = CORPUS_DIR) -> Path:
    return corpus_dir / "chunks" / f"{source.source_id}.jsonl"


def fetch(source: SourceDocument, corpus_dir: Path = CORPUS_DIR) -> Path:
    """Download the source PDF unless a verified copy exists. Fails on a checksum mismatch."""
    path = raw_path(source, corpus_dir)
    if path.exists():
        verify_sha256(path, source.sha256)
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(".part")
    with httpx.stream("GET", source.url, follow_redirects=True, timeout=120) as response:
        response.raise_for_status()
        with partial.open("wb") as file:
            for block in response.iter_bytes():
                file.write(block)
    try:
        verify_sha256(partial, source.sha256)
    except ValueError:
        partial.unlink()
        raise
    partial.rename(path)
    return path


def build(source: SourceDocument, corpus_dir: Path = CORPUS_DIR) -> Path:
    pdf = raw_path(source, corpus_dir)
    verify_sha256(pdf, source.sha256)
    chunks = build_chunks(source, read_pdf_pages(pdf))
    out = chunks_path(source, corpus_dir)
    write_chunks(chunks, out)
    print(f"{source.source_id}: {len(chunks)} chunks -> {out}")
    return out


async def ingest_sources(
    database_url: str, model_names: Sequence[str], corpus_dir: Path, cache_dir: str | None
) -> None:
    pool = await open_pool(database_url)
    try:
        for name in model_names:
            spec = model_spec(name)
            store = PgKnowledgeStore(pool, spec)
            await store.ensure_schema()
            embedder = FastEmbedEmbedder(spec, cache_dir=cache_dir)
            for source in SOURCES.values():
                chunks = load_chunks(chunks_path(source, corpus_dir))
                report = await ingest(store, embedder, source.source_id, chunks)
                print(
                    f"{source.source_id} [{spec.slug}]: {report.upserted} chunks, "
                    f"{report.removed} removed, {report.embedded} embedded"
                )
    finally:
        await pool.close()


async def evaluate(
    database_url: str,
    model_names: Sequence[str],
    questions_path: Path,
    corpus_dir: Path,
    cache_dir: str | None,
) -> str:
    """Score each model in dense and hybrid mode, and lexical search once (it uses no model)."""
    questions = load_questions(questions_path)
    chunk_pages = {
        chunk.chunk_id: chunk.printed_pages
        for source in SOURCES.values()
        for chunk in load_chunks(chunks_path(source, corpus_dir))
    }
    relevant = {q.question_id: relevant_chunk_ids(q, chunk_pages) for q in questions}
    unanswerable = [qid for qid, ids in relevant.items() if not ids]
    if unanswerable:
        raise ValueError(f"questions with no relevant chunk: {', '.join(unanswerable)}")

    results: dict[tuple[str, str], Summary] = {}
    latency: dict[tuple[str, str], float] = {}
    pool = await open_pool(database_url)
    try:
        for index, name in enumerate(model_names):
            spec = model_spec(name)
            embedder = FastEmbedEmbedder(spec, cache_dir=cache_dir)
            await embedder.warm_up()
            store = PgKnowledgeStore(pool, spec)
            modes = ("dense", "hybrid", "lexical") if index == 0 else ("dense", "hybrid")
            for mode in modes:
                retriever = KnowledgeRetriever(embedder, store, mode=mode)
                scores, timings = [], []
                for question in questions:
                    started = time.perf_counter()
                    ranked = await retriever.retrieve(question.question, max(DEFAULT_KS))
                    timings.append((time.perf_counter() - started) * 1000)
                    ids = [chunk.chunk_id for chunk in ranked]
                    scores.append(score_ranking(ids, relevant[question.question_id]))
                key = ("(none)" if mode == "lexical" else name, mode)
                results[key] = summarize(scores)
                latency[key] = statistics.median(timings)
                print(f"{key[0]} {mode}: MRR {results[key].mrr:.3f}")
    finally:
        await pool.close()
    context = (
        f"Run {date.today().isoformat()} on {len(chunk_pages)} chunks and {len(questions)} "
        f"questions (`{questions_path}`). Questions are colloquial Peruvian Spanish written and "
        "labelled by the assistant, not reviewed by clinicians. Latency includes the local query "
        "embedding on CPU."
    )
    return render_report(results, latency_ms=latency, context=context)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="puente-knowledge", description=__doc__)
    parser.add_argument("--corpus-dir", type=Path, default=CORPUS_DIR)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("fetch", help="download the source PDFs and verify their SHA-256")
    commands.add_parser("build", help="extract and chunk the source PDFs into JSONL")
    ingest_parser = commands.add_parser("ingest", help="load the chunks into PostgreSQL")
    models = ingest_parser.add_mutually_exclusive_group()
    models.add_argument("--model", help="embedding model (default: PUENTE_EMBEDDING_MODEL)")
    models.add_argument("--all-models", action="store_true", help="index every known model")
    eval_parser = commands.add_parser("eval", help="score retrieval on the labelled questions")
    eval_parser.add_argument("--questions", type=Path, default=QUESTIONS_PATH)
    eval_parser.add_argument("--out", type=Path, help="report path (default: eval/reports/)")
    args = parser.parse_args(argv)

    if args.command == "eval":
        settings = get_settings()
        if settings.database_url is None:
            parser.error("PUENTE_DATABASE_URL is not set")
        report = asyncio.run(
            evaluate(
                settings.database_url.get_secret_value(),
                list(KNOWN_MODELS),
                args.questions,
                args.corpus_dir,
                settings.embedding_cache_dir,
            )
        )
        out = args.out or REPORTS_DIR / f"retrieval-{date.today().isoformat()}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"report -> {out}")
        return 0

    if args.command == "ingest":
        settings = get_settings()
        if settings.database_url is None:
            parser.error("PUENTE_DATABASE_URL is not set")
        names = list(KNOWN_MODELS) if args.all_models else [args.model or settings.embedding_model]
        asyncio.run(
            ingest_sources(
                settings.database_url.get_secret_value(),
                names,
                args.corpus_dir,
                settings.embedding_cache_dir,
            )
        )
        return 0

    for source in SOURCES.values():
        if args.command == "fetch":
            print(f"{source.source_id}: {fetch(source, args.corpus_dir)}")
        elif args.command == "build":
            build(source, args.corpus_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
