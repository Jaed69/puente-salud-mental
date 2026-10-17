import asyncio
import json

import httpx
import pytest
from pydantic import SecretStr

from puente.companion.openai_compatible import OpenAICompatibleChatModel
from puente.companion.ports import ChatModelError, ChatModelTimeoutError

MESSAGES = [
    {"role": "system", "content": "sistema"},
    {"role": "user", "content": "hola"},
]


def _ok(content: object = "Hola, aquí estoy.") -> dict[str, object]:
    return {"choices": [{"index": 0, "message": {"role": "assistant", "content": content}}]}


def _model(handler, **overrides) -> OpenAICompatibleChatModel:
    options: dict[str, object] = {
        "base_url": "https://llm.example.test/api/v1",
        "model": "provider/model:free",
        "api_key": SecretStr("sk-test"),
        "timeout_seconds": 5.0,
        "max_output_tokens": 123,
        "transport": httpx.MockTransport(handler),
    }
    options.update(overrides)
    return OpenAICompatibleChatModel(**options)


def test_complete_posts_openai_chat_completions_request_and_returns_text():
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=_ok("  Hola, aquí estoy.  "))

    reply = asyncio.run(_model(handler).complete(MESSAGES))

    assert reply == "Hola, aquí estoy."
    (request,) = seen
    assert request.method == "POST"
    assert str(request.url) == "https://llm.example.test/api/v1/chat/completions"
    assert request.headers["authorization"] == "Bearer sk-test"
    payload = json.loads(request.content)
    assert payload["model"] == "provider/model:free"
    assert payload["messages"] == MESSAGES
    assert payload["max_tokens"] == 123
    assert payload["stream"] is False


def test_trailing_slash_in_base_url_is_normalized():
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=_ok())

    model = _model(handler, base_url="https://llm.example.test/v1beta/openai/")
    asyncio.run(model.complete(MESSAGES))

    assert str(seen[0].url) == "https://llm.example.test/v1beta/openai/chat/completions"


def test_missing_api_key_sends_no_authorization_header():
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=_ok())

    asyncio.run(_model(handler, api_key=None).complete(MESSAGES))

    assert "authorization" not in seen[0].headers


def test_http_error_status_maps_to_chat_model_error_without_body():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="rate limited, echo: secreto-prompt")

    with pytest.raises(ChatModelError) as excinfo:
        asyncio.run(_model(handler).complete(MESSAGES))

    assert "429" in str(excinfo.value)
    assert "secreto-prompt" not in str(excinfo.value)


def test_timeout_maps_to_chat_model_timeout_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(ChatModelTimeoutError):
        asyncio.run(_model(handler).complete(MESSAGES))


def test_transport_failure_maps_to_chat_model_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    with pytest.raises(ChatModelError):
        asyncio.run(_model(handler).complete(MESSAGES))


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, text="not json"),
        httpx.Response(200, json={"choices": []}),
        httpx.Response(200, json={"unexpected": True}),
        httpx.Response(200, json=_ok(None)),
        httpx.Response(200, json=_ok(["not", "text"])),
    ],
)
def test_malformed_response_maps_to_chat_model_error(response):
    def handler(_request: httpx.Request) -> httpx.Response:
        return response

    with pytest.raises(ChatModelError):
        asyncio.run(_model(handler).complete(MESSAGES))


def test_timeout_error_is_a_chat_model_error():
    assert issubclass(ChatModelTimeoutError, ChatModelError)
