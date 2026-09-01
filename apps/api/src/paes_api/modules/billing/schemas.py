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
    #: False mientras los límites se informen pero no bloqueen, porque todavía
    #: no se puede contratar el plan Pro.
    limites_activos: bool


class CanjearIn(BaseModel):
    codigo: str = Field(min_length=3, max_length=40)


class ProductoOut(BaseModel):
    """Un producto comprable, tal como se muestra en la página."""

    id: str
    plan: str
    dias: int
    monto: int
    asunto: str


class ProductosOut(BaseModel):
    #: False cuando faltan las credenciales de Flow. La web usa esto para no
    #: mostrar un botón de pago que llevaría a un error.
    pago_disponible: bool
    productos: list[ProductoOut]


class PagarIn(BaseModel):
    #: Solo el identificador del producto. El monto NUNCA viaja desde el
    #: cliente: lo fija el servidor.
    producto: str


class PagarOut(BaseModel):
    #: URL de Flow a la que hay que enviar al usuario.
    url: str
    orden: str


class TrialOut(BaseModel):
    """La URL de Flow donde el usuario registra su tarjeta para empezar el trial."""

    url: str
