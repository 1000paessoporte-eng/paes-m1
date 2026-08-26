from pydantic import BaseModel

from paes_api.modules.content.models import Difficulty
from paes_api.modules.skill_tree.models import SkillAxis, Subject


class DemoAlternativeOut(BaseModel):
    """Sin is_correct: misma regla de integridad que el Modo Examen."""

    id: int
    label: str
    text: str


class DemoPassageOut(BaseModel):
    """Texto base de una pregunta de Competencia Lectora.

    Va en la demo por la misma razón que en el examen: la pregunta de lectora
    no se puede responder sin el texto. Antes la demo sorteaba entre todas las
    preguntas del banco y podía mostrar una de lectora huérfana, imposible de
    contestar.
    """

    id: int
    title: str
    body: str
    kind: str
    source_note: str | None = None


class DemoQuestionOut(BaseModel):
    id: int
    difficulty: Difficulty
    stem: str
    #: Figura de la pregunta, cuando la tiene. Va por la misma razón que el
    #: texto de Lectora: hay preguntas que no se pueden contestar sin ella, y
    #: la demo es la primera pantalla que ve alguien sin cuenta.
    image_url: str | None = None
    #: Prueba y eje del temario a los que pertenece la pregunta. La demo los
    #: expone para poder cerrar con un desglose por eje —"fallaste 2 de 2 en
    #: Geometría"— en vez de un porcentaje suelto que no dice qué estudiar.
    subject: Subject
    axis: SkillAxis
    #: El eje ya escrito para mostrar ("Álgebra y Funciones"). Sale del
    #: mismo diccionario que usa el resultado del ensayo: si el nombre de un
    #: eje cambia, cambia en los dos lugares a la vez.
    axis_label: str
    #: Nombre del nodo del árbol ("Proporcionalidad", "Función cuadrática").
    node_name: str
    #: Código del nodo, para enlazar la lección pública correspondiente.
    node_code: str
    passage: DemoPassageOut | None = None
    alternatives: list[DemoAlternativeOut]


class DemoAnswerIn(BaseModel):
    question_id: int
    selected_alternative_id: int | None = None


class DemoGradeIn(BaseModel):
    answers: list[DemoAnswerIn]


class DemoGradeItemOut(BaseModel):
    question_id: int
    is_correct: bool
    correct_alternative_id: int
    explanation: str | None = None
    #: La alternativa que marcó quien responde. Viaja de vuelta para que la
    #: pantalla no tenga que recordarla por su cuenta.
    selected_alternative_id: int | None = None
    #: El error conceptual que lleva justo a la alternativa marcada
    #: ("Entregó el avance horizontal en lugar de la pendiente"). Es lo que la
    #: portada promete —"el razonamiento exacto que te llevó a la alternativa
    #: incorrecta"— y hasta ahora la demo no lo devolvía: quien probaba sin
    #: cuenta veía la resolución genérica y nunca su propio error.
    #: Va solo cuando se falló; en una respuesta correcta no hay distractor.
    distractor_justification: str | None = None


class DemoGradeOut(BaseModel):
    items: list[DemoGradeItemOut]
    correct: int
    total: int
