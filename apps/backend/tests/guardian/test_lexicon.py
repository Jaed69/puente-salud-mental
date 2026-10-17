import pytest

from puente.guardian.lexicon import Category, detect, normalize


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  Ya   NO quiero estar AQUÍ  ", "ya no quiero estar aqui"),
        ("Quiero hacerme daño", "quiero hacerme dano"),
        ("¿¡Me quiero MATAR!?", "me quiero matar"),
        ("línea\t\n113", "linea 113"),
    ],
)
def test_normalize_lowercases_strips_accents_punctuation_and_whitespace(raw, expected):
    assert normalize(raw) == expected


@pytest.mark.parametrize(
    "text",
    [
        "quiero morir",
        "Ya me quiero morir, no aguanto",
        "me quiero matar",
        "a veces pienso en matarme",
        "quiero matarm",
        "no quiero vivir más",
        "he pensado en quitarme la vida",
        "quiero acabar con todo",
        "sería mejor no existir",
        "ya no quiero estar aquí",
        "pienso en el suicidio",
        "pienso en el suisidio",
        "me voy a matar",
    ],
)
def test_detects_suicidal_ideation(text):
    assert Category.SUICIDAL_IDEATION in detect(text)


@pytest.mark.parametrize(
    "text",
    ["quiero cortarme", "tengo ganas de hacerme daño", "necesito lastimarme"],
)
def test_detects_self_harm(text):
    assert Category.SELF_HARM in detect(text)


@pytest.mark.parametrize(
    "text",
    ["ya tengo las pastillas", "esta noche me voy a tirar del puente"],
)
def test_detects_plan_or_means(text):
    assert Category.PLAN_OR_MEANS in detect(text)


@pytest.mark.parametrize(
    "text",
    [
        "mi pareja me quiere matar",
        "me quieren matar",
        "me está golpeando",
        "me amenazó con matarme",
    ],
)
def test_detects_violence_from_others(text):
    categories = detect(text)
    assert Category.VIOLENCE in categories
    assert Category.SUICIDAL_IDEATION not in categories


@pytest.mark.parametrize(
    "text",
    [
        "me muero de risa",
        "me mata el calor",
        "estoy muerto de cansancio",
        "este examen me va a matar",
        "hoy me siento un poco triste",
        "me voy a cortar el pelo",
        "quiero acabar con todo el trabajo hoy",
        "",
    ],
)
def test_does_not_flag_common_figurative_or_neutral_phrases(text):
    assert detect(text) == frozenset()
