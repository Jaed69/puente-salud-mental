"""Chat model port: the only contract the companion needs from an LLM provider (no I/O here)."""

from collections.abc import Sequence
from typing import Literal, Protocol, TypedDict


class ChatMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatModelError(Exception):
    """The chat model could not produce a reply. Messages never include prompt or output text."""


class ChatModelTimeoutError(ChatModelError):
    """The chat model did not answer in time."""


class ChatModelPort(Protocol):
    async def complete(self, messages: Sequence[ChatMessage]) -> str:
        """Return the assistant reply for ``messages`` or raise ``ChatModelError``."""
        ...
