from enum import StrEnum

from pydantic import BaseModel, EmailStr


class LeadSource(StrEnum):
    """De dónde salió el correo.

    Cerrado a propósito: si fuera texto libre, cada pantalla nueva inventaría
    su propia etiqueta y el conteo por origen dejaría de significar algo.

    Hoy solo la demo pide el correo, así que hay un valor. Se agrega el que
    corresponda cuando una segunda pantalla empiece a pedirlo -- declarar
    ahora orígenes que nadie produce solo ensucia el conteo.
    """

    DEMO = "demo"


class LeadIn(BaseModel):
    email: EmailStr
    source: LeadSource = LeadSource.DEMO


class LeadOut(BaseModel):
    """Respuesta deliberadamente pobre.

    No devuelve el id ni si el correo ya estaba: el endpoint es público y sin
    autenticación, así que cualquier diferencia observable entre "nuevo" y "ya
    existía" convierte esto en un oráculo para averiguar quién está en la
    lista.
    """

    ok: bool = True
