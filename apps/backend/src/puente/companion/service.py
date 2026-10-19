"""Companion service: builds the safety system prompt and asks the chat model for a reply.

The companion is a supportive listener, never a therapist: it does not diagnose and it points to
Línea 113, opción 5 when there is risk. Crisis handling itself never depends on this service; the
guardian handles it before and after the model call.
"""

import asyncio
from collections.abc import Sequence

from puente.companion.ports import ChatMessage, ChatModelPort

MAX_HISTORY_MESSAGES = 10

SYSTEM_PROMPT = (
    "Eres Puente, un acompañante de apoyo emocional dentro de una aplicación. "
    "No eres terapeuta, ni psicólogo, ni médico, ni una persona: eres un asistente de inteligencia "
    "artificial, y lo dices con honestidad si te lo preguntan. "
    "Responde siempre en español neutro, con calidez y sin juzgar, en pocas frases "
    "(máximo cuatro). "
    "Escucha, valida lo que la persona siente y haz como mucho una pregunta abierta. "
    "Puedes sugerir hábitos de autocuidado sencillos y respaldados por evidencia, como respirar "
    "lento, hacer pausas, moverse con suavidad, cuidar el sueño o hablar con alguien de confianza. "
    "Nunca hagas diagnósticos, no uses nombres de trastornos para describir a la persona y no "
    "recomiendes medicamentos ni dosis. "
    "Si el malestar es intenso o se mantiene en el tiempo, anima a buscar ayuda de un profesional "
    "de salud mental. "
    "Si la persona menciona peligro o riesgo para su vida, recomiéndale llamar gratis a la "
    "Línea 113, opción 5, que atiende las 24 horas. "
    "No inventes datos, servicios ni números de teléfono."
)


class CompanionUnavailableError(Exception):
    """The companion could not produce a usable reply. Never carries conversation text."""


class CompanionService:
    def __init__(self, model: ChatModelPort, *, timeout_seconds: float) -> None:
        self._model = model
        self._timeout_seconds = timeout_seconds

    async def reply(self, text: str, history: Sequence[ChatMessage] = ()) -> str:
        """Return the companion reply or raise ``CompanionUnavailableError``."""
        messages = build_messages(text, history)
        try:
            raw = await asyncio.wait_for(self._model.complete(messages), self._timeout_seconds)
        except Exception as exc:
            raise CompanionUnavailableError(type(exc).__name__) from exc
        reply = raw.strip() if isinstance(raw, str) else ""
        if not reply:
            raise CompanionUnavailableError("empty reply")
        return reply


def build_messages(text: str, history: Sequence[ChatMessage] = ()) -> list[ChatMessage]:
    recent = list(history)[-MAX_HISTORY_MESSAGES:]
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *recent,
        {"role": "user", "content": text},
    ]
