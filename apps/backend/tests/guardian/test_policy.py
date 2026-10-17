from puente.guardian import lexicon
from puente.guardian.policy import (
    GUARDIAN_ERROR,
    GuardDecision,
    assess,
    build_crisis_response,
    safe_assess,
)


def test_assess_returns_none_for_neutral_message():
    decision = assess("hoy fue un día normal")

    assert decision.risk == "none"
    assert decision.categories == ()


def test_assess_returns_crisis_with_categories():
    decision = assess("me quiero matar")

    assert decision.risk == "crisis"
    assert "suicidal_ideation" in decision.categories


def test_safe_assess_fails_closed_when_detector_raises(monkeypatch):
    def boom(_text):
        raise RuntimeError("detector exploded")

    monkeypatch.setattr(lexicon, "detect", boom)

    decision = safe_assess("hoy fue un día normal")

    assert decision.risk == "crisis"
    assert decision.categories == (GUARDIAN_ERROR,)


def test_safe_assess_does_not_log_message_text(monkeypatch, caplog):
    secret = "texto privado del usuario"

    def boom(_text):
        raise ValueError(secret)

    monkeypatch.setattr(lexicon, "detect", boom)

    with caplog.at_level("DEBUG"):
        safe_assess(secret)

    assert secret not in caplog.text


def test_crisis_response_points_to_113_option_5_first():
    response = build_crisis_response(assess("quiero morir"))

    assert "113" in response.message
    assert "opción 5" in response.message
    assert response.resources[0].number == "113"
    assert response.resources[0].option == "5"


def test_crisis_response_for_violence_prioritizes_police_and_linea_100():
    response = build_crisis_response(assess("mi pareja me quiere matar"))

    numbers = [r.number for r in response.resources]
    assert numbers[:2] == ["105", "100"]
    assert "113" in numbers


def test_crisis_response_for_guardian_error_uses_general_crisis_resources():
    decision = GuardDecision(risk="crisis", categories=(GUARDIAN_ERROR,))

    response = build_crisis_response(decision)

    assert response.resources[0].number == "113"
    assert "113" in response.message


def test_crisis_response_never_contains_method_details():
    response = build_crisis_response(assess("ya tengo las pastillas"))

    assert "pastilla" not in response.message.lower()


def test_crisis_response_for_violence_with_self_risk_uses_general_script():
    decision = assess("me pegan y ya no quiero vivir")
    assert {"violence", "suicidal_ideation"} <= set(decision.categories)

    response = build_crisis_response(decision)

    assert response.resources[0].number == "113"
    assert response.resources[0].option == "5"
    assert "opción 5" in response.message
    assert response.message.startswith("Gracias por contármelo")
