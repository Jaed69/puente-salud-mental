"""Message endpoint: every message passes the guardian before anything else.

Flow: guardian on the input -> crisis response without calling the model, or the companion reply
-> guardian on the model output (fail closed) -> reply. When the model is unavailable the endpoint
serves a fixed, non-LLM fallback reply.

Message text, history, prompts and model output are sensitive personal data (Ley 29733): they are
never logged. Only exception type names are logged.
"""

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, StringConstraints

from puente.companion.ports import ChatMessage, ChatModelPort
from puente.companion.service import CompanionService
from puente.guardian.policy import GuardDecision, build_crisis_response, safe_assess
from puente.guardian.resources import CrisisResource, ResourceNote

MAX_MESSAGE_LENGTH = 4000
MAX_HISTORY_ITEMS = 10

# Fixed reply when the model is not configured, fails, times out or returns no text.
COMPANION_FALLBACK = (
    "Gracias por escribir. En este momento no puedo responderte como quisiera, pero tu mensaje "
    "importa. Si en algún momento sientes que estás en peligro, llama gratis a la Línea 113, "
    "opción 5, que atiende las 24 horas."
)

logger = logging.getLogger(__name__)

# Last-resort crisis payload, built only from literals so it cannot fail at request time.
STATIC_CRISIS_PAYLOAD: dict[str, object] = {
    "type": "crisis",
    "message": (
        "No tienes que pasar por esto a solas. Llama ahora a la Línea 113, opción 5: es gratuita "
        "y atiende las 24 horas. Si estás en peligro inmediato, llama al 106 (SAMU)."
    ),
    "resources": [
        {
            "id": "minsa_113_5",
            "name": "Línea 113, opción 5",
            "number": "113",
            "option": "5",
            "organization": "MINSA",
            "purpose": "Apoyo en salud mental",
            "availability": "24/7",
            "free": True,
            "verified": True,
            "source": "Press citing MINSA, 2025.",
        },
        {
            "id": "samu_106",
            "name": "SAMU 106",
            "number": "106",
            "option": None,
            "organization": "MINSA - SAMU",
            "purpose": "Emergencias médicas",
            "availability": None,
            "free": None,
            "verified": False,
            "source": "Pending confirmation against gob.pe or the owning institution.",
        },
    ],
    "note": {
        "text": (
            "Si estás en riesgo de suicidio, puedes acudir directamente a un Centro de Salud "
            "Mental Comunitario, sin referencia."
        ),
        "source": "https://www.gob.pe/10942",
    },
}

router = APIRouter(prefix="/v1")


MessageText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_MESSAGE_LENGTH),
]


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    text: MessageText


class MessageIn(BaseModel):
    text: MessageText
    history: Annotated[tuple[HistoryItem, ...], Field(max_length=MAX_HISTORY_ITEMS)] = ()


class CrisisOut(BaseModel):
    type: Literal["crisis"] = "crisis"
    message: str
    resources: tuple[CrisisResource, ...]
    note: ResourceNote


class ReplyOut(BaseModel):
    type: Literal["reply"] = "reply"
    message: str


def get_chat_model(request: Request) -> ChatModelPort | None:
    """The configured chat model, or ``None``. Tests override this dependency with a fake."""
    return getattr(request.app.state, "chat_model", None)


@router.post("/messages", response_model=CrisisOut | ReplyOut)
async def post_message(
    body: MessageIn,
    request: Request,
    chat_model: Annotated[ChatModelPort | None, Depends(get_chat_model)],
) -> CrisisOut | ReplyOut | JSONResponse:
    decision = safe_assess(body.text)
    if decision.risk == "crisis":
        return _crisis_out(decision)
    if chat_model is None:
        return ReplyOut(message=COMPANION_FALLBACK)

    try:
        companion = CompanionService(
            chat_model, timeout_seconds=request.app.state.settings.llm_timeout_seconds
        )
        reply = await companion.reply(body.text, _history_messages(body.history))
    except Exception as exc:
        logger.warning("Companion unavailable (%s); serving fallback reply.", type(exc).__name__)
        return ReplyOut(message=COMPANION_FALLBACK)

    # Layer 1 on the model output too: a reply that trips the lexicon, or a failed check, is
    # replaced by the fixed crisis response.
    output_decision = safe_assess(reply)
    if output_decision.risk == "crisis":
        return _crisis_out(output_decision)
    return ReplyOut(message=reply)


def _history_messages(history: tuple[HistoryItem, ...]) -> list[ChatMessage]:
    return [{"role": item.role, "content": item.text} for item in history]


def _crisis_out(decision: GuardDecision) -> CrisisOut | JSONResponse:
    """Build the crisis reply, failing closed to a static payload. Never logs text or messages."""
    try:
        crisis = build_crisis_response(decision)
        return CrisisOut(message=crisis.message, resources=crisis.resources, note=crisis.note)
    except Exception as exc:
        logger.error(
            "Crisis response build failed (%s); serving static payload.", type(exc).__name__
        )
        return JSONResponse(content=STATIC_CRISIS_PAYLOAD)
