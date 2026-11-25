"""Command line for the knowledge base: ``puente-knowledge fetch|build``.

Run from ``apps/backend``. Paths default to the committed ``corpus/`` layout.
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx

from puente.knowledge.corpus import (
    DWM_SOURCE,
    SourceDocument,
    build_chunks,
    read_pdf_pages,
    verify_sha256,
    write_chunks,
)

SOURCES: dict[str, SourceDocument] = {DWM_SOURCE.source_id: DWM_SOURCE}
CORPUS_DIR = Path("corpus")


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="puente-knowledge", description=__doc__)
    parser.add_argument("--corpus-dir", type=Path, default=CORPUS_DIR)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("fetch", help="download the source PDFs and verify their SHA-256")
    commands.add_parser("build", help="extract and chunk the source PDFs into JSONL")
    args = parser.parse_args(argv)

    for source in SOURCES.values():
        if args.command == "fetch":
            print(f"{source.source_id}: {fetch(source, args.corpus_dir)}")
        elif args.command == "build":
            build(source, args.corpus_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
