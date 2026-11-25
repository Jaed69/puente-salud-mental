import asyncio
import os
import time

import pytest
from fastapi.testclient import TestClient

from puente import main
from puente.config import Settings
from puente.main import attach_knowledge, create_app


def _settings(**values) -> Settings:
    return Settings(_env_file=None, environment="test", **values)


UNREACHABLE = "postgresql://puente:wrong@127.0.0.1:1/puente"


class StubEmbedder:
    def __init__(self, spec, **_kwargs):
        self.spec = spec

    async def warm_up(self):
        return None


class FailingEmbedder(StubEmbedder):
    async def warm_up(self):
        raise RuntimeError("model download failed")


def test_health_is_unchanged():
    with TestClient(create_app(_settings())) as client:
        assert client.get("/health").json() == {"status": "ok"}


def test_ready_reports_knowledge_disabled_without_a_database():
    with TestClient(create_app(_settings())) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "knowledge": "disabled"}


def test_unreachable_database_degrades_readiness_but_keeps_serving():
    settings = _settings(database_url=UNREACHABLE, database_connect_timeout=1)

    with TestClient(create_app(settings)) as client:
        ready = client.get("/ready")
        reply = client.post("/v1/messages", json={"text": "hola"}).json()

    assert ready.status_code == 503
    assert ready.json()["status"] == "degraded"
    assert ready.json()["knowledge"] in {"starting", "unavailable"}
    assert reply["type"] == "reply"


def test_startup_does_not_wait_for_the_knowledge_base(monkeypatch):
    started = asyncio.Event()

    class SlowEmbedder(StubEmbedder):
        async def warm_up(self):
            started.set()
            await asyncio.sleep(30)

    async def fake_pool(*_args, **_kwargs):
        return FakePool()

    monkeypatch.setattr(main, "FastEmbedEmbedder", SlowEmbedder)
    monkeypatch.setattr(main, "open_pool", fake_pool)
    settings = _settings(database_url="postgresql://unused/db")

    with TestClient(create_app(settings)) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/ready").json() == {"status": "degraded", "knowledge": "starting"}


class FakePool:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_attach_failure_after_the_pool_opens_closes_the_pool(monkeypatch):
    pool = FakePool()

    async def fake_pool(*_args, **_kwargs):
        return pool

    monkeypatch.setattr(main, "FastEmbedEmbedder", FailingEmbedder)
    monkeypatch.setattr(main, "open_pool", fake_pool)
    app = create_app(_settings(database_url="postgresql://unused/db"))

    attached = await attach_knowledge(app, app.state.settings)

    assert attached is None
    assert pool.closed
    assert app.state.retriever is None
    assert app.state.knowledge_status == "unavailable"


@pytest.mark.asyncio
async def test_attach_success_enables_the_retriever(monkeypatch):
    pool = FakePool()

    async def fake_pool(*_args, **_kwargs):
        return pool

    monkeypatch.setattr(main, "FastEmbedEmbedder", StubEmbedder)
    monkeypatch.setattr(main, "open_pool", fake_pool)
    app = create_app(_settings(database_url="postgresql://unused/db"))

    attached = await attach_knowledge(app, app.state.settings)

    assert attached is pool
    assert not pool.closed
    assert app.state.retriever is not None
    assert app.state.knowledge_status == "ready"


@pytest.mark.skipif(
    not os.environ.get("PUENTE_TEST_DATABASE_URL"), reason="PUENTE_TEST_DATABASE_URL is not set"
)
def test_reachable_database_enables_the_retriever(monkeypatch):
    monkeypatch.setattr(main, "FastEmbedEmbedder", StubEmbedder)
    settings = _settings(database_url=os.environ["PUENTE_TEST_DATABASE_URL"])

    with TestClient(create_app(settings)) as client:
        for _ in range(50):
            if client.get("/ready").status_code == 200:
                break
            time.sleep(0.1)
        assert client.get("/ready").json() == {"status": "ok", "knowledge": "ready"}
