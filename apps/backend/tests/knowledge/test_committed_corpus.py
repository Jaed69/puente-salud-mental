"""Contract of the committed corpus: what the store and the companion may rely on."""

import hashlib
from pathlib import Path

import pytest

from puente.knowledge.cli import chunks_path, fetch, raw_path
from puente.knowledge.corpus import DWM_SOURCE, SourceDocument, load_chunks

BACKEND_DIR = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def chunks():
    return load_chunks(chunks_path(DWM_SOURCE, BACKEND_DIR / "corpus"))


def test_committed_chunks_have_unique_ids_and_text(chunks):
    ids = [chunk.chunk_id for chunk in chunks]

    assert len(chunks) > 40
    assert len(ids) == len(set(ids))
    assert all(chunk.text.strip() for chunk in chunks)


def test_committed_chunks_are_lay_material_with_attribution(chunks):
    assert {chunk.audience for chunk in chunks} == {"lay"}
    assert {chunk.content_type for chunk in chunks}.isdisjoint({"dosing", "diagnostic"})
    assert all("CC BY-NC-SA 3.0 IGO" in chunk.attribution for chunk in chunks)


def test_committed_chunks_exclude_the_licence_front_matter(chunks):
    assert not any("Notas de descargo" in chunk.text for chunk in chunks)
    assert not any("ISBN" in chunk.text for chunk in chunks)


def _source_with(sha256: str) -> SourceDocument:
    return SourceDocument(**{**DWM_SOURCE.__dict__, "sha256": sha256, "url": "http://invalid"})


def test_fetch_reuses_a_verified_local_copy_without_network(tmp_path):
    source = _source_with(hashlib.sha256(b"pdf").hexdigest())
    path = raw_path(source, tmp_path)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"pdf")

    assert fetch(source, tmp_path) == path


def test_fetch_rejects_a_tampered_local_copy(tmp_path):
    source = _source_with(hashlib.sha256(b"pdf").hexdigest())
    path = raw_path(source, tmp_path)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"otro")

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        fetch(source, tmp_path)
