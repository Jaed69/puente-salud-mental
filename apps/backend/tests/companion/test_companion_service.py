import asyncio

import pytest

from puente.companion.ports import ChatModelError
from puente.companion.service import (
    MAX_HISTORY_MESSAGES,
    SYSTEM_PROMPT,
    CompanionService,
    CompanionUnavailableError,
)


class FakeChatModel:
    def __init__(self, reply: str = "Te escucho.", error: Exception | None = None) -> None:
        self.reply = reply
        self.error = error
        self.calls: list[list[dict[str, str]]] = []

    async def complete(self, messages):
        self.calls.append(list(messages))
        if self.error is not None:
            raise self.error
        return self.reply


class SlowChatModel:
    async def complete(self, _messages):
        await asyncio.sleep(10)
        return "demasiado tarde"


def test_reply_sends_system_prompt_history_and_current_text():
    model = FakeChatModel(reply="  Gracias por contarme.  ")
    service = CompanionService(model, timeout_seconds=5)
    history = [
        {"role": "user", "content": "hola"},
        {"role": "assistant", "content": "hola, ¿cómo estás?"},
    ]

    reply = asyncio.run(service.reply("estoy cansado", history))

    assert reply == "Gracias por contarme."
    (messages,) = model.calls
    assert messages[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert messages[1:3] == history
    assert messages[-1] == {"role": "user", "content": "estoy cansado"}


def test_reply_keeps_only_the_most_recent_history():
    model = FakeChatModel()
    service = CompanionService(model, timeout_seconds=5)
    history = [{"role": "user", "content": f"m{i}"} for i in range(MAX_HISTORY_MESSAGES + 5)]

    asyncio.run(service.reply("ahora", history))

    sent = model.calls[0]
    assert len(sent) == MAX_HISTORY_MESSAGES + 2
    assert sent[1]["content"] == "m5"


def test_system_prompt_sets_safety_boundaries():
    prompt = SYSTEM_PROMPT.lower()

    assert "no eres terapeuta" in prompt
    assert "diagn" in prompt
    assert "113" in prompt
    assert "opción 5" in prompt
    assert "profesional" in prompt


@pytest.mark.parametrize("reply", ["", "   \n "])
def test_empty_model_reply_raises_unavailable(reply):
    service = CompanionService(FakeChatModel(reply=reply), timeout_seconds=5)

    with pytest.raises(CompanionUnavailableError):
        asyncio.run(service.reply("hola"))


def test_model_error_raises_unavailable():
    service = CompanionService(FakeChatModel(error=ChatModelError("boom")), timeout_seconds=5)

    with pytest.raises(CompanionUnavailableError):
        asyncio.run(service.reply("hola"))


def test_slow_model_raises_unavailable_after_timeout():
    service = CompanionService(SlowChatModel(), timeout_seconds=0.05)

    with pytest.raises(CompanionUnavailableError):
        asyncio.run(service.reply("hola"))
