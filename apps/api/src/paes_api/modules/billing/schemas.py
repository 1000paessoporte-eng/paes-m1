from datetime import datetime

from pydantic import BaseModel, Field

from paes_api.modules.billing.models import Plan


class MiPlanOut(BaseModel):
    """El plan del usuario y lo que puede hacer con él."""

    plan: Plan
    vence_el: datetime | None = None
    #: Cuántos ensayos lleva este mes y cuántos permite su plan (null = sin tope).
    ensayos_usados: int
    ensayos_limite: int | None
    carreras_limite: int
    analisis_avanzado: bool
    #: False mientras los límites se informen pero no bloqueen, porque todavía
    #: no se puede contratar el plan Pro.
    limites_activos: bool


class CanjearIn(BaseModel):
    codigo: str = Field(min_length=3, max_length=40)
