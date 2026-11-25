"""Grounding: numbered reference material for the prompt, and validation of the model's citations.

The model cites references as ``[n]``. Only numbers of chunks that were actually retrieved count as
sources; every marker, valid or not, is removed from the text shown to the person.
"""

import re
from collections.abc import Sequence

from puente.knowledge.ports import RetrievedChunk

REFERENCE_INSTRUCTIONS = (
    "Material de referencia: fragmentos de la guía de la OMS «En tiempos de estrés, haz lo que "
    "importa». Úsalos solo si ayudan con lo que la persona cuenta. Explica la idea con tus "
    "palabras, sin copiar párrafos. Si usas una idea de un fragmento, cita su número entre "
    "corchetes, por ejemplo [1]. No cites números que no aparezcan aquí. Este material no "
    "reemplaza la ayuda de un profesional ni sirve para diagnosticar."
)

# A marker with the spaces before it, so "lento [1]." becomes "lento." and nothing else changes.
_MARKER = re.compile(r"[ \t]*\[(\d{1,2}(?:\s*,\s*\d{1,2})*)\]")


def format_pages(pages: Sequence[int]) -> str:
    if not pages:
        return ""
    return f"{pages[0]}" if len(pages) == 1 else f"{pages[0]}-{pages[-1]}"


def build_reference_block(references: Sequence[RetrievedChunk]) -> str:
    if not references:
        return ""
    entries = []
    for number, chunk in enumerate(references, start=1):
        label = "pág." if len(chunk.printed_pages) == 1 else "págs."
        pages = format_pages(chunk.printed_pages)
        entries.append(f"[{number}] {chunk.section_title}, {label} {pages}\n{chunk.text}")
    return REFERENCE_INSTRUCTIONS + "\n\n" + "\n\n".join(entries)


def resolve_citations(
    text: str, references: Sequence[RetrievedChunk]
) -> tuple[str, list[RetrievedChunk]]:
    """Return the text without citation markers and the cited references, in citation order."""
    cited: list[RetrievedChunk] = []
    for match in _MARKER.finditer(text):
        for number in match.group(1).split(","):
            index = int(number) - 1
            if 0 <= index < len(references) and references[index] not in cited:
                cited.append(references[index])
    if not _MARKER.search(text):
        return text, cited
    return _MARKER.sub("", text).strip(), cited
