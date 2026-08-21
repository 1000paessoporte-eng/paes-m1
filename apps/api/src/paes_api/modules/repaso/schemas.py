from datetime import date

from pydantic import BaseModel

from paes_api.modules.content.models import Difficulty


class RepasoAlternativaOut(BaseModel):
    id: int
    label: str
    text: str


class RepasoPreguntaOut(BaseModel):
    """Una pregunta de la sesión. Sin `is_correct` en las alternativas: la
    corrección la hace el servidor al responder, como en práctica."""

    question_id: int
    difficulty: Difficulty
    stem: str
    image_url: str | None = None
    #: El texto base, cuando la pregunta es de Competencia Lectora. Sin él la
    #: pregunta no se entiende: en Lectora la respuesta está en el texto.
    passage: str | None = None
    passage_title: str | None = None
    node_name: str
    alternatives: list[RepasoAlternativaOut]
    #: Cuántas veces la ha fallado. Se muestra: saber que es la tercera vez es
    #: lo que convierte "otra pregunta" en "esta es la que se me resiste".
    veces_fallada: int
    #: En qué peldaño de la escalera va, para dibujar el avance.
    nivel: int


class RepasoSesionOut(BaseModel):
    preguntas: list[RepasoPreguntaOut]
    #: Cuántas quedan vencidas más allá de las que trae esta sesión.
    pendientes_totales: int


class RepasoRespuestaIn(BaseModel):
    question_id: int
    selected_alternative_id: int


class RepasoRespuestaOut(BaseModel):
    is_correct: bool
    correct_alternative_id: int
    explanation: str | None = None
    #: Por qué la alternativa que eligió induce al error. Solo cuando falló.
    distractor_justification: str | None = None
    #: Cuándo vuelve esta pregunta. NULL cuando la dominó.
    proxima_fecha: date | None = None
    #: True cuando acaba de salir de la cola para siempre.
    dominada: bool = False
    nivel: int
    #: Nodos del árbol que esta respuesta acaba de desbloquear. Repasar mueve
    #: el árbol igual que practicar, y desbloquear un tema es la mejor noticia
    #: que puede dar esta pantalla.
    newly_unlocked: list[str] = []


class RepasoResumenOut(BaseModel):
    """Los tres números de la tarjeta del panel."""

    pendientes_hoy: int
    en_repaso: int
    dominadas: int
    #: Cuándo vuelve a haber algo que repasar, si hoy no hay nada.
    proxima_fecha: date | None = None
