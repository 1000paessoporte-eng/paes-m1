from datetime import datetime

from pydantic import BaseModel, Field


class ErrorClienteIn(BaseModel):
    """Lo que manda el navegador cuando algo revienta.

    Todo viene acotado: el payload llega de internet sin sesión y no puede
    servir para escribir megabytes en la base.
    """

    mensaje: str = Field(max_length=500)
    ruta: str = Field(max_length=255)
    pila: str | None = Field(default=None, max_length=4000)


class ErrorClienteOut(BaseModel):
    mensaje: str
    ruta: str
    pila: str | None
    navegador: str | None
    veces: int
    ocurrido_en: datetime
    #: Cuántas cuentas distintas lo sufrieron. Un error que le pasa a uno es
    #: un caso raro; el mismo a veinte es lo primero que hay que arreglar.
    usuarios: int
