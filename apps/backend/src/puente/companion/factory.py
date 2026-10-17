"""Builds the configured chat model from settings, or ``None`` when no model is configured."""

from puente.companion.openai_compatible import OpenAICompatibleChatModel
from puente.companion.ports import ChatModelPort
from puente.config import Settings


def build_chat_model(settings: Settings) -> ChatModelPort | None:
    if not settings.llm_base_url or not settings.llm_model:
        return None
    return OpenAICompatibleChatModel(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        timeout_seconds=settings.llm_timeout_seconds,
        max_output_tokens=settings.llm_max_output_tokens,
    )
