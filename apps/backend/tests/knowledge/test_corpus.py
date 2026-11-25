import hashlib

import pytest

from puente.knowledge.corpus import (
    DWM_SOURCE,
    BookSection,
    SourceDocument,
    build_chunks,
    clean_page_text,
    verify_sha256,
)


def test_clean_page_text_drops_running_header_and_page_number():
    raw = "Parte 1: PONER LOS PIES EN LA TIERRA\nBébela tan \ndespacio \ncomo puedas.\n31\n"

    assert clean_page_text(raw, header="Parte 1: PONER LOS PIES EN LA TIERRA") == (
        "Bébela tan despacio como puedas."
    )


def test_clean_page_text_joins_hyphenated_words_and_collapses_whitespace():
    raw = "Es una habi-\nlidad   que \n\n se aprende \n"

    assert clean_page_text(raw) == "Es una habilidad que se aprende"


def test_clean_page_text_expands_typographic_ligatures_for_lexical_search():
    cleaned = clean_page_text("Una «tormenta» signiﬁca\nque ﬂuye")

    assert cleaned == "Una «tormenta» significa que fluye"


def test_clean_page_text_keeps_short_real_words():
    raw = "O si te has quedado sin\ningresos...\nY también\n"

    assert clean_page_text(raw) == "O si te has quedado sin ingresos... Y también"


def _source(sections: tuple[BookSection, ...]) -> SourceDocument:
    return SourceDocument(
        source_id="test-book",
        title="Libro de prueba",
        publisher="Editorial",
        year=2020,
        licence="CC BY-NC-SA 3.0 IGO",
        attribution="Libro de prueba. Editorial; 2020. Licencia: CC BY-NC-SA 3.0 IGO.",
        url="https://example.org/book.pdf",
        sha256="0" * 64,
        printed_page_offset=2,
        sections=sections,
    )


def _pages(count: int) -> dict[int, str]:
    return {number: f"texto de la página {number}" for number in range(1, count + 1)}


def test_build_chunks_windows_pages_with_one_page_overlap_inside_a_section():
    source = _source(
        (BookSection("p1", "Parte 1: Uno", first_page=3, last_page=7, content_type="exercise"),)
    )

    chunks = build_chunks(source, _pages(10), window=3, stride=2)

    assert [chunk.pdf_pages for chunk in chunks] == [(3, 4, 5), (5, 6, 7)]
    assert [chunk.printed_pages for chunk in chunks] == [(1, 2, 3), (3, 4, 5)]
    assert chunks[0].text == "texto de la página 3 texto de la página 4 texto de la página 5"


def test_build_chunks_never_crosses_sections_and_keeps_the_tail():
    source = _source(
        (
            BookSection("p1", "Parte 1: Uno", first_page=3, last_page=6, content_type="exercise"),
            BookSection("p2", "Parte 2: Dos", first_page=7, last_page=7, content_type="exercise"),
        )
    )

    chunks = build_chunks(source, _pages(10), window=3, stride=2)

    assert [(chunk.section_id, chunk.pdf_pages) for chunk in chunks] == [
        ("p1", (3, 4, 5)),
        ("p1", (5, 6)),
        ("p2", (7,)),
    ]


def test_build_chunks_sets_stable_ids_and_lay_metadata():
    source = _source(
        (BookSection("p1", "Parte 1: Uno", first_page=3, last_page=5, content_type="exercise"),)
    )

    (chunk,) = build_chunks(source, _pages(10), window=3, stride=2)

    assert chunk.chunk_id == "test-book:p1:001-003"
    assert chunk.source_id == "test-book"
    assert chunk.section_title == "Parte 1: Uno"
    assert chunk.audience == "lay"
    assert chunk.content_type == "exercise"
    assert chunk.licence == "CC BY-NC-SA 3.0 IGO"
    assert chunk.attribution.startswith("Libro de prueba")
    assert chunk.embedding_text.startswith("Libro de prueba — Parte 1: Uno\n")


def test_build_chunks_skips_pages_without_text():
    source = _source(
        (BookSection("p1", "Parte 1: Uno", first_page=3, last_page=5, content_type="exercise"),)
    )
    pages = _pages(10) | {4: "   ", 5: ""}

    (chunk,) = build_chunks(source, pages, window=3, stride=2)

    assert chunk.pdf_pages == (3,)


def test_dwm_source_indexes_no_front_matter_and_no_clinical_content_types():
    first_indexed = min(section.first_page for section in DWM_SOURCE.sections)

    assert first_indexed >= 10  # pages 1-9: cover, licence, index, preface, acknowledgements
    assert {section.content_type for section in DWM_SOURCE.sections} <= {
        "overview",
        "exercise",
        "summary",
    }


def test_verify_sha256_accepts_matching_file(tmp_path):
    path = tmp_path / "book.pdf"
    path.write_bytes(b"contenido")

    verify_sha256(path, hashlib.sha256(b"contenido").hexdigest())


def test_verify_sha256_rejects_a_different_file(tmp_path):
    path = tmp_path / "book.pdf"
    path.write_bytes(b"otro contenido")

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        verify_sha256(path, hashlib.sha256(b"contenido").hexdigest())
