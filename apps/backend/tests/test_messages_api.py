import pytest
from fastapi.testclient import TestClient

from puente.config import Settings
from puente.guardian import lexicon
from puente.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(Settings(environment="test")))


def test_crisis_message_returns_fixed_crisis_response(client):
    response = client.post("/v1/messages", json={"text": "ya no quiero vivir"})

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "crisis"
    assert "113" in body["message"]
    assert body["resources"][0]["number"] == "113"
    assert body["resources"][0]["option"] == "5"


def test_neutral_message_returns_placeholder_reply(client):
    response = client.post("/v1/messages", json={"text": "hoy me fue bien en el trabajo"})

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "reply"
    assert "todavía no está disponible" in body["message"]
    assert "resources" not in body


def test_guardian_failure_returns_crisis_response(client, monkeypatch):
    def boom(_text):
        raise RuntimeError("detector exploded")

    monkeypatch.setattr(lexicon, "detect", boom)

    response = client.post("/v1/messages", json={"text": "hola"})

    assert response.status_code == 200
    assert response.json()["type"] == "crisis"


@pytest.mark.parametrize(
    "payload",
    [{}, {"text": ""}, {"text": "   "}, {"text": "a" * 4001}, {"text": 123}],
)
def test_invalid_payload_is_rejected(client, payload):
    response = client.post("/v1/messages", json=payload)

    assert response.status_code == 422


def test_message_text_is_never_logged(client, caplog):
    secret = "me quiero matar secreto-unico-xyz"

    with caplog.at_level("DEBUG"):
        client.post("/v1/messages", json={"text": secret})
        client.post("/v1/messages", json={"text": "neutral secreto-unico-xyz"})

    assert "secreto-unico-xyz" not in caplog.text


def test_crisis_response_builder_failure_returns_static_crisis_payload(client, monkeypatch, caplog):
    from puente.api import messages

    def boom(_decision):
        raise RuntimeError("builder exploded secreto-builder")

    monkeypatch.setattr(messages, "build_crisis_response", boom)

    with caplog.at_level("DEBUG"):
        response = client.post("/v1/messages", json={"text": "ya no quiero vivir secreto-msg"})

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "crisis"
    assert "113" in body["message"]
    assert "opción 5" in body["message"]
    assert "106" in body["message"]
    assert body["resources"][0]["number"] == "113"
    assert body["resources"][0]["option"] == "5"
    assert "secreto-msg" not in caplog.text
    assert "secreto-builder" not in caplog.text
