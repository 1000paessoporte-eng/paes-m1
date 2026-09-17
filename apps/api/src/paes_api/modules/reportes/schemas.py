from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

#: Las razones por las que un alumno diría que una pregunta está mal.
#:
#: Son cinco y no una caja de texto libre porque el reporte se hace en medio de
#: un ensayo: elegir es un toque, escribir son treinta segundos que nadie va a
#: gastar. La categoría además es lo que permite ordenar la bandeja --un
#: "la respuesta correcta está mal" se mira antes que un "se ve mal en mi
#: teléfono".
Motivo = Literal[
    "respuesta_incorrecta",
    "varias_correctas",
    "enunciado_confuso",
    "datos_erroneos",
    "otro",
]

#: Desde dónde se reportó.
Contexto = Literal["ensayo", "revision", "practica"]


class ReporteIn(BaseModel):
    question_id: int
    motivo: Motivo
    #: Opcional: el botón tiene que poder usarse sin escribir nada.
    comentario: str | None = Field(default=None, max_length=500)
    contexto: Contexto


class ReportePreguntaOut(BaseModel):
    """Una pregunta reportada, con todos sus avisos juntos.

    El panel agrupa por pregunta porque lo que se arregla es la pregunta: tres
    alumnos avisando de la misma es una sola cosa que hacer, y el orden en que
    hay que hacerlas lo da cuánta gente avisó.
    """

    question_id: int
    #: El enunciado, para poder decidir sin salir del panel.
    stem: str
    skill_node_name: str
    #: La alternativa marcada como correcta en el banco. Es lo primero que se
    #: mira cuando alguien dice que la clave está mal.
    respuesta_correcta: str | None
    reportes: int
    pendientes: int
    #: Cuántas veces se eligió cada motivo, de mayor a menor.
    motivos: dict[str, int]
    comentarios: list["ComentarioOut"]
    ultimo_en: datetime


class ComentarioOut(BaseModel):
    motivo: str
    comentario: str | None
    contexto: str
    creado_en: datetime
    revisado_en: datetime | None
