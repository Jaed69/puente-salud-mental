"""Deterministic crisis lexicon for Peruvian and neutral Spanish (guardian layer 1).

SEED LIST: these patterns are an initial, non-exhaustive draft written by engineers. They MUST be
reviewed and extended by Peruvian clinicians before any real user relies on them. The lexicon is
deliberately biased toward recall: a false positive shows crisis resources, a false negative can
cost a life.

Patterns run over normalized text (see ``normalize``): lowercase, no accents or diacritics (so
"ñ" becomes "n"), punctuation replaced by spaces and whitespace collapsed.
"""

import re
import unicodedata
from enum import StrEnum


class Category(StrEnum):
    SUICIDAL_IDEATION = "suicidal_ideation"
    SELF_HARM = "self_harm"
    PLAN_OR_MEANS = "plan_or_means"
    VIOLENCE = "violence"


# First-person intent in front of "matar(me)" (also tolerates the truncated "matarm").
_SELF_INTENT = r"(?:quiero|quisiera|voy a|pienso en|pense en|ganas de|deseo|intentar|intente)"
# Someone else threatening the person.
_OTHER_INTENT = r"(?:quiere|quieren|amenaza con|amenazo con|amenazan con|amenazaron con)"

CRISIS_PATTERNS: dict[Category, tuple[str, ...]] = {
    Category.SUICIDAL_IDEATION: (
        r"\b(?:me )?(?:quiero|quisiera|deseo) morir(?:me)?\b",
        r"\bme quiero matar\b",
        r"\bme voy a matar\b",
        rf"\b{_SELF_INTENT} matarme?\b",
        r"\bno quiero (?:seguir )?vivir\b",
        r"\bquitarme la vida\b",
        r"\bquitarse la vida\b",
        r"\bacabar con mi vida\b",
        r"\bacabar con todo\b(?! (?:el|la|los|las|lo) )",
        r"\bmejor no existir\b",
        r"\bno quiero existir\b",
        r"\bya no quiero estar aqui\b",
        r"\bsui[cs]id",
        r"\bno vale la pena vivir\b",
        r"\bdesaparecer para siempre\b",
    ),
    Category.SELF_HARM: (
        r"\bcortarme\b(?! (?:el|la|las|los) (?:pelo|cabello|unas|barba|flequillo)\b)",
        r"\bme corto (?:las venas|los brazos|las munecas)\b",
        r"\bhacerme dano\b",
        r"\blastimarme\b",
        r"\bautolesion",
    ),
    Category.PLAN_OR_MEANS: (
        r"\btengo (?:las|unas) pastillas\b",
        r"\bme voy a tirar\b(?! (?:a|en) (?:la cama|el sofa|dormir)\b)",
        r"\bme voy a (?:lanzar|aventar|colgar|ahorcar)\b",
        r"\bvoy a tomar(?:me)? (?:todas )?las pastillas\b",
        r"\btomar veneno\b",
    ),
    Category.VIOLENCE: (
        r"\bme (?:quiere|quieren) matar\b",
        rf"\b{_OTHER_INTENT} matarme?\b",
        r"\bme (?:amenaza|amenazan|amenazo|amenazaron) de muerte\b",
        r"\bme (?:esta|estan) (?:pegando|golpeando|amenazando)\b",
        r"\bme (?:pega|pegan|golpea|golpean|maltrata|maltratan)\b",
        r"\bme (?:violo|violaron|abusa|abusan)\b",
    ),
}

_COMPILED: dict[Category, tuple[re.Pattern[str], ...]] = {
    category: tuple(re.compile(p) for p in patterns)
    for category, patterns in CRISIS_PATTERNS.items()
}

_NON_WORD = re.compile(r"[^a-z0-9]+")


def normalize(text: str) -> str:
    """Lowercase, strip accents and diacritics, drop punctuation and collapse whitespace."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return _NON_WORD.sub(" ", without_marks).strip()


def detect(text: str) -> frozenset[Category]:
    """Return every crisis category whose patterns match the message."""
    normalized = normalize(text)
    if not normalized:
        return frozenset()
    return frozenset(
        category
        for category, patterns in _COMPILED.items()
        if any(p.search(normalized) for p in patterns)
    )
