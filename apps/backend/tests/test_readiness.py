import os

import pytest
from fastapi.testclient import TestClient

from puente.config import Settings
from puente.main import create_app


def _settings(**values) -> Settings:
    return Settings(_env_file=None, environment="test", **values)


def test_health_is_unchanged():
    with TestClient(create_app(_settings())) as client:
        assert client.get("/health").json() == {"status": "ok"}


def test_ready_reports_knowledge_disabled_without_a_database():
    with TestClient(create_app(_settings())) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "knowledge": "disabled"}


def test_unreachable_database_leaves_the_app_serving_without_knowledge():
    settings = _settings(
        database_url="postgresql://puente:wrong@127.0.0.1:1/puente", database_connect_timeout=1
    )

    with TestClient(create_app(settings)) as client:
        ready = client.get("/ready").json()
        reply = client.post("/v1/messages", json={"text": "hola"}).json()

    assert ready == {"status": "ok", "knowledge": "unavailable"}
    assert reply["type"] == "reply"


@pytest.mark.skipif(
    not os.environ.get("PUENTE_TEST_DATABASE_URL"), reason="PUENTE_TEST_DATABASE_URL is not set"
)
def test_reachable_database_enables_the_retriever(monkeypatch):
    from puente import main

    class StubEmbedder:
        def __init__(self, spec, **_kwargs):
            self.spec = spec

        async def warm_up(self):
            return None

    monkeypatch.setattr(main, "FastEmbedEmbedder", StubEmbedder)
    settings = _settings(database_url=os.environ["PUENTE_TEST_DATABASE_URL"])

    with TestClient(create_app(settings)) as client:
        assert client.get("/ready").json() == {"status": "ok", "knowledge": "ready"}
        assert client.app.state.retriever is not None
