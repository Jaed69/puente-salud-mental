from fastapi.testclient import TestClient

from puente.config import Settings
from puente.main import create_app


def test_health_returns_ok() -> None:
    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_settings_read_env_prefix(monkeypatch) -> None:
    monkeypatch.setenv("PUENTE_ENVIRONMENT", "production")

    assert Settings().environment == "production"
