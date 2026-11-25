from puente.companion.grounding import build_reference_block, resolve_citations
from puente.knowledge.ports import RetrievedChunk


def _ref(chunk_id: str, pages=(100, 101, 102), text="Háblate con amabilidad.") -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        source_id="who-dwm-2020-es",
        source_title="En tiempos de estrés, haz lo que importa: una guía ilustrada",
        section_title="Parte 4: Ser amable",
        printed_pages=pages,
        text=text,
        attribution="OMS; 2020. Licencia: CC BY-NC-SA 3.0 IGO.",
        url="https://www.who.int/x.pdf",
        score=0.03,
        rank=1,
    )


KIND = _ref("who:p4:100-102")
BREATH = _ref("who:h1:122-122", pages=(122,), text="Respira lento y presiona los pies.")


def test_reference_block_numbers_each_chunk_with_section_and_pages():
    block = build_reference_block([KIND, BREATH])

    assert "[1] Parte 4: Ser amable, págs. 100-102" in block
    assert "Háblate con amabilidad." in block
    assert "[2] Parte 4: Ser amable, pág. 122" in block
    assert "cita su número entre corchetes" in block


def test_reference_block_is_empty_without_references():
    assert build_reference_block([]) == ""


def test_resolve_citations_keeps_cited_references_and_strips_markers():
    text, cited = resolve_citations(
        "Prueba respirar lento [2]. Y háblate con cariño [1].", [KIND, BREATH]
    )

    assert text == "Prueba respirar lento. Y háblate con cariño."
    assert cited == [BREATH, KIND]


def test_resolve_citations_handles_grouped_and_repeated_markers():
    text, cited = resolve_citations("Dos ideas [1, 2] y otra vez [1][2].", [KIND, BREATH])

    assert text == "Dos ideas y otra vez."
    assert cited == [KIND, BREATH]


def test_resolve_citations_drops_numbers_that_were_not_retrieved():
    text, cited = resolve_citations("Algo inventado [3] y algo real [1].", [KIND])

    assert text == "Algo inventado y algo real."
    assert cited == [KIND]


def test_resolve_citations_without_references_strips_every_marker():
    text, cited = resolve_citations("Respira [1].", [])

    assert text == "Respira."
    assert cited == []


def test_resolve_citations_leaves_text_without_markers_untouched():
    text, cited = resolve_citations("Te escucho. ¿Qué pasó hoy?", [KIND])

    assert text == "Te escucho. ¿Qué pasó hoy?"
    assert cited == []


def test_resolve_citations_only_touches_the_markers():
    text, _ = resolve_citations("Mira :) esto ( sí ) importa [1].\nAdemás: algo.", [KIND])

    assert text == "Mira :) esto ( sí ) importa.\nAdemás: algo."


def test_format_pages_of_an_empty_sequence_is_empty():
    from puente.companion.grounding import format_pages

    assert format_pages(()) == ""
