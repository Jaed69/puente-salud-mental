"""Message endpoint: every message passes the guardian before anything else.

Message text is sensitive personal data (Ley 29733): it is never logged.
"""

import logging
from typing import Annotated, Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StringConstraints

from puente.guardian.policy import GuardDecision, build_crisis_response, safe_assess
from puente.guardian.resources import CrisisResource, ResourceNote

MAX_MESSAGE_LENGTH = 4000

COMPANION_PLACEHOLDER = (
    "Gracias por escribir. El acompañante conversacional todavía no está disponible. "
    "Si en algún momento sientes que estás en peligro, llama gratis a la Línea 113, opción 5."
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


class MessageIn(BaseModel):
    text: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_MESSAGE_LENGTH),
    ]


class CrisisOut(BaseModel):
    type: Literal["crisis"] = "crisis"
    message: str
    resources: tuple[CrisisResource, ...]
    note: ResourceNote


class ReplyOut(BaseModel):
    type: Literal["reply"] = "reply"
    message: str


@router.post("/messages", response_model=CrisisOut | ReplyOut)
def post_message(body: MessageIn) -> CrisisOut | ReplyOut | JSONResponse:
    decision = safe_assess(body.text)
    if decision.risk == "crisis":
        return _crisis_out(decision)
    return ReplyOut(message=COMPANION_PLACEHOLDER)


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
