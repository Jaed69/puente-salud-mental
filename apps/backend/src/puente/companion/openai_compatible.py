"""Adapter for any OpenAI-compatible ``/chat/completions`` endpoint.

One adapter covers OpenRouter, Cloudflare Workers AI, Groq, Gemini's OpenAI compatibility layer and
similar providers: only the base URL, API key and model name change. Error messages never include
request or response bodies, because both may contain sensitive conversation text.
"""

from collections.abc import Sequence

import httpx
from pydantic import SecretStr

from puente.companion.ports import ChatMessage, ChatModelError, ChatModelTimeoutError


class OpenAICompatibleChatModel:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: SecretStr | None = None,
        timeout_seconds: float = 20.0,
        max_output_tokens: int = 300,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._url = f"{base_url.rstrip('/')}/chat/completions"
        self._model = model
        self._api_key = api_key
        self._timeout = httpx.Timeout(timeout_seconds)
        self._max_output_tokens = max_output_tokens
        self._transport = transport

    async def complete(self, messages: Sequence[ChatMessage]) -> str:
        payload = {
            "model": self._model,
            "messages": list(messages),
            "max_tokens": self._max_output_tokens,
            "stream": False,
        }
        headers = {}
        if self._api_key is not None:
            headers["Authorization"] = f"Bearer {self._api_key.get_secret_value()}"

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout, transport=self._transport
            ) as client:
                response = await client.post(self._url, json=payload, headers=headers)
        except httpx.TimeoutException as exc:
            raise ChatModelTimeoutError("chat model request timed out") from exc
        except httpx.HTTPError as exc:
            raise ChatModelError(f"chat model transport error ({type(exc).__name__})") from exc

        if response.is_error:
            raise ChatModelError(f"chat model returned HTTP {response.status_code}")
        return _extract_text(response)


def _extract_text(response: httpx.Response) -> str:
    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise ChatModelError("chat model returned a malformed response") from exc
    if not isinstance(content, str):
        raise ChatModelError("chat model returned no text content")
    return content.strip()
