"""Corpus: turns a licensed source document into citable, audience-tagged chunks.

Pure functions plus thin file helpers. Chunks follow the book structure: consecutive pages of one
section are grouped in overlapping windows and never cross a section boundary, and each summary
page is its own chunk. Front matter (cover, licence, acknowledgements) is never indexed.
"""

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

ContentType = Literal["overview", "exercise", "summary", "dosing", "diagnostic"]
Audience = Literal["lay", "clinician", "helper"]

DEFAULT_WINDOW = 3
DEFAULT_STRIDE = 2


@dataclass(frozen=True)
class BookSection:
    section_id: str
    title: str
    first_page: int
    last_page: int
    content_type: ContentType
    header: str | None = None
    """Running header printed on every page of the section, removed during cleaning."""


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    title: str
    publisher: str
    year: int
    licence: str
    attribution: str
    url: str
    sha256: str
    printed_page_offset: int
    """PDF page number minus the page number printed in the book."""
    sections: tuple[BookSection, ...]
    audience: Audience = "lay"


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source_id: str
    source_title: str
    section_id: str
    section_title: str
    pdf_pages: tuple[int, ...]
    printed_pages: tuple[int, ...]
    text: str
    embedding_text: str
    audience: Audience
    content_type: ContentType
    licence: str
    attribution: str
    url: str


_DWM_PARTS = (
    ("p1", "Parte 1: Poner los pies en la tierra", 13, 53, "Parte 1: PONER LOS PIES EN LA TIERRA"),
    ("p2", "Parte 2: Desengancharse", 55, 80, "Parte 2: DESENGANCHARSE"),
    (
        "p3",
        "Parte 3: Actuar de acuerdo con tus valores",
        82,
        100,
        "Parte 3: ACTUAR DE ACUERDO CON TUS VALORES",
    ),
    ("p4", "Parte 4: Ser amable", 102, 108, "Parte 4: SER AMABLE"),
    ("p5", "Parte 5: Dejar espacio", 110, 123, "Parte 5: DEJAR ESPACIO"),
)

_DWM_TOOLS = (
    (124, "Resumen, herramienta 1: Poner los pies en la tierra"),
    (125, "Resumen, herramienta 2: Desengancharse"),
    (126, "Resumen, herramienta 3: Actuar de acuerdo con tus valores"),
    (127, "Resumen, herramienta 4: Ser amable"),
    (128, "Resumen, herramienta 5: Dejar espacio"),
)

DWM_SOURCE = SourceDocument(
    source_id="who-dwm-2020-es",
    title="En tiempos de estrés, haz lo que importa: una guía ilustrada",
    publisher="Organización Mundial de la Salud",
    year=2020,
    licence="CC BY-NC-SA 3.0 IGO",
    attribution=(
        "En tiempos de estrés, haz lo que importa: una guía ilustrada [Doing what matters in "
        "times of stress: an illustrated guide]. Ginebra: Organización Mundial de la Salud; 2020. "
        "Licencia: CC BY-NC-SA 3.0 IGO."
    ),
    url="https://www.who.int/docs/default-source/mental-health/sh-2020-spa-3-web.pdf",
    sha256="db06ef3a89220f15e9431d66a35b8754b871092fbd5415b719e00465601f5df8",
    printed_page_offset=2,
    sections=(
        BookSection("intro", "Introducción: cómo usar este libro", 10, 11, "overview"),
        *(
            BookSection(section_id, title, first, last, "exercise", header)
            for section_id, title, first, last, header in _DWM_PARTS
        ),
        *(
            BookSection(f"h{index}", title, page, page, "summary", "Resumen")
            for index, (page, title) in enumerate(_DWM_TOOLS, start=1)
        ),
    ),
)

_PAGE_NUMBER = re.compile(r"^\d{1,3}$")
_HYPHENATED_BREAK = re.compile(r"(\w)-\n(\w)")
_WHITESPACE = re.compile(r"\s+")


def clean_page_text(raw: str, header: str | None = None) -> str:
    """Return one page's text as a single line, without running header or page number."""
    header_key = _normalize(header) if header else None
    kept = []
    # NFKC expands ligatures such as "ﬁ" so full-text search matches "significa".
    for line in unicodedata.normalize("NFKC", raw).splitlines():
        stripped = line.strip()
        if not stripped or _PAGE_NUMBER.match(stripped):
            continue
        if header_key is not None and _normalize(stripped) == header_key:
            continue
        kept.append(stripped)
    joined = _HYPHENATED_BREAK.sub(r"\1\2", "\n".join(kept))
    return _WHITESPACE.sub(" ", joined).strip()


def build_chunks(
    source: SourceDocument,
    pages: Mapping[int, str],
    *,
    window: int = DEFAULT_WINDOW,
    stride: int = DEFAULT_STRIDE,
) -> list[Chunk]:
    """Group the cleaned pages of each section into overlapping windows of ``window`` pages."""
    if window < 1 or not 1 <= stride <= window:
        raise ValueError("window must be >= 1 and stride between 1 and window")
    chunks: list[Chunk] = []
    for section in source.sections:
        for window_pages in _windows(section.first_page, section.last_page, window, stride):
            texts = {
                page: clean_page_text(pages.get(page, ""), section.header) for page in window_pages
            }
            kept = tuple(page for page in window_pages if texts[page])
            if not kept:
                continue
            chunks.append(_chunk(source, section, kept, " ".join(texts[page] for page in kept)))
    return chunks


def _windows(first: int, last: int, window: int, stride: int) -> Iterable[tuple[int, ...]]:
    start = first
    while True:
        end = min(start + window - 1, last)
        yield tuple(range(start, end + 1))
        if end >= last:
            return
        start += stride


def _chunk(
    source: SourceDocument, section: BookSection, pdf_pages: tuple[int, ...], text: str
) -> Chunk:
    printed = tuple(page - source.printed_page_offset for page in pdf_pages)
    return Chunk(
        chunk_id=f"{source.source_id}:{section.section_id}:{printed[0]:03d}-{printed[-1]:03d}",
        source_id=source.source_id,
        source_title=source.title,
        section_id=section.section_id,
        section_title=section.title,
        pdf_pages=pdf_pages,
        printed_pages=printed,
        text=text,
        embedding_text=f"{source.title} — {section.title}\n{text}",
        audience=source.audience,
        content_type=section.content_type,
        licence=source.licence,
        attribution=source.attribution,
        url=source.url,
    )


def _normalize(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip().casefold()


def read_pdf_pages(path: Path) -> dict[int, str]:
    """Return the raw text of every page, keyed by 1-based PDF page number."""
    import logging

    from pypdf import PdfReader

    # pypdf warns about font encodings on every page of this InDesign export; text is unaffected.
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    reader = PdfReader(path)
    return {number: page.extract_text() or "" for number, page in enumerate(reader.pages, 1)}


def verify_sha256(path: Path, expected: str) -> None:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected:
        raise ValueError(f"SHA-256 mismatch for {path.name}: expected {expected}, got {digest}")


def write_chunks(chunks: Iterable[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = (json.dumps(asdict(chunk), ensure_ascii=False) for chunk in chunks)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_chunks(path: Path) -> list[Chunk]:
    chunks = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        data["pdf_pages"] = tuple(data["pdf_pages"])
        data["printed_pages"] = tuple(data["printed_pages"])
        chunks.append(Chunk(**data))
    return chunks
