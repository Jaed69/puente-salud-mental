"""Peru crisis resources as typed data.

Only Linea 113 opcion 5 is marked verified (press citing MINSA, 2025). Every other entry must be
confirmed against gob.pe or the owning institution before a real user sees it. WhatsApp or chat
channels are intentionally absent: none has been verified.
"""

from pydantic import BaseModel, ConfigDict

_PENDING = "Pending confirmation against gob.pe or the owning institution."


class CrisisResource(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    number: str
    option: str | None = None
    organization: str
    purpose: str
    availability: str | None = None
    free: bool | None = None
    verified: bool
    source: str


class ResourceNote(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str
    source: str


LINEA_113_SALUD_MENTAL = CrisisResource(
    id="minsa_113_5",
    name="Línea 113, opción 5",
    number="113",
    option="5",
    organization="MINSA",
    purpose="Apoyo en salud mental",
    availability="24/7",
    free=True,
    verified=True,
    source="Press citing MINSA, 2025.",
)

SAMU_106 = CrisisResource(
    id="samu_106",
    name="SAMU 106",
    number="106",
    organization="MINSA - SAMU",
    purpose="Emergencias médicas",
    verified=False,
    source=_PENDING,
)

PNP_105 = CrisisResource(
    id="pnp_105",
    name="Policía Nacional 105",
    number="105",
    organization="PNP",
    purpose="Peligro inmediato o violencia",
    verified=False,
    source=_PENDING,
)

BOMBEROS_116 = CrisisResource(
    id="bomberos_116",
    name="Bomberos 116",
    number="116",
    organization="Cuerpo General de Bomberos Voluntarios del Perú",
    purpose="Emergencias y rescate",
    verified=False,
    source=_PENDING,
)

LINEA_100 = CrisisResource(
    id="mimp_100",
    name="Línea 100",
    number="100",
    organization="MIMP",
    purpose="Orientación ante violencia familiar o sexual",
    verified=False,
    source=_PENDING,
)

CRISIS_RESOURCES: tuple[CrisisResource, ...] = (
    LINEA_113_SALUD_MENTAL,
    SAMU_106,
    PNP_105,
    BOMBEROS_116,
    LINEA_100,
)

COMMUNITY_MENTAL_HEALTH_NOTE = ResourceNote(
    text=(
        "Si estás en riesgo de suicidio, puedes acudir directamente a un Centro de Salud Mental "
        "Comunitario, sin referencia."
    ),
    source="https://www.gob.pe/10942",
)
