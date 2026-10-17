"""Message endpoint: every message passes the guardian before anything else.

Message text is sensitive personal data (Ley 29733): it is never logged.
"""

from typing import Annotated, Literal

from fastapi import APIRouter
from pydantic import BaseModel, StringConstraints

from puente.guardian.policy import build_crisis_response, safe_assess
from puente.guardian.resources import CrisisResource, ResourceNote

MAX_MESSAGE_LENGTH = 4000

COMPANION_PLACEHOLDER = (
    "Gracias por escribir. El acompañante conversacional todavía no está disponible. "
    "Si en algún momento sientes que estás en peligro, llama gratis a la Línea 113, opción 5."
)

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
def post_message(body: MessageIn) -> CrisisOut | ReplyOut:
    decision = safe_assess(body.text)
    if decision.risk == "crisis":
        crisis = build_crisis_response(decision)
        return CrisisOut(message=crisis.message, resources=crisis.resources, note=crisis.note)
    return ReplyOut(message=COMPANION_PLACEHOLDER)
