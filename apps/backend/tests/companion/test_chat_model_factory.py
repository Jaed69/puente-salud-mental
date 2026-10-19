import pytest

from puente.companion.factory import build_chat_model
from puente.companion.openai_compatible import OpenAICompatibleChatModel
from puente.config import Settings


def _settings(**values) -> Settings:
    return Settings(_env_file=None, environment="test", **values)


@pytest.mark.parametrize(
    "values",
    [
        {},
        {"llm_base_url": "https://openrouter.ai/api/v1"},
        {"llm_model": "provider/model:free"},
    ],
)
def test_unconfigured_settings_build_no_model(values):
    assert build_chat_model(_settings(**values)) is None


def test_configured_settings_build_openai_compatible_model():
    model = build_chat_model(
        _settings(
            llm_base_url="https://openrouter.ai/api/v1",
            llm_model="provider/model:free",
            llm_api_key="sk-test",
        )
    )

    assert isinstance(model, OpenAICompatibleChatModel)


def test_llm_settings_read_env_prefix_and_hide_api_key(monkeypatch):
    monkeypatch.setenv("PUENTE_LLM_BASE_URL", "https://api.groq.com/openai/v1")
    monkeypatch.setenv("PUENTE_LLM_MODEL", "some-model")
    monkeypatch.setenv("PUENTE_LLM_API_KEY", "sk-secret-value")
    monkeypatch.setenv("PUENTE_LLM_TIMEOUT_SECONDS", "7.5")

    settings = Settings(_env_file=None)

    assert settings.llm_base_url == "https://api.groq.com/openai/v1"
    assert settings.llm_model == "some-model"
    assert settings.llm_timeout_seconds == 7.5
    assert settings.llm_api_key is not None
    assert settings.llm_api_key.get_secret_value() == "sk-secret-value"
    assert "sk-secret-value" not in repr(settings)


def test_llm_timeout_defaults_to_twenty_seconds():
    assert _settings().llm_timeout_seconds == 20.0
