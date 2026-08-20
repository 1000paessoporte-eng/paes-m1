from pydantic import BaseModel, ConfigDict

from paes_api.modules.skill_tree.models import ProgressStatus, SkillAxis, Subject


class SkillNodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    axis: SkillAxis
    subject: Subject
    tier: int
    unlock_threshold: float
    display_order: int
    prerequisite_codes: list[str] = []
    #: Los nombres de esos prerrequisitos. Van con el nodo porque la pantalla
    #: filtra por prueba: los prerrequisitos de M2 son nodos de M1, que no
    #: vienen en la misma respuesta, y sin esto la tarjeta terminaba mostrando
    #: el código interno ("Requiere: num_racionales") al estudiante.
    prerequisite_names: list[str] = []


class SkillNodeProgressOut(SkillNodeOut):
    status: ProgressStatus
    accuracy: float
    attempts: int
    #: Si el nodo tiene teoría escrita. La interfaz ofrece "Aprender" solo
    #: cuando la hay; el resto lleva directo a practicar.
    has_lesson: bool = False


class LessonStepOut(BaseModel):
    accion: str
    porque: str


class LessonOut(BaseModel):
    """La teoría del nodo: lo que se estudia antes de practicar."""

    model_config = ConfigDict(from_attributes=True)

    node_code: str
    node_name: str
    intro: str
    theory: str
    example_statement: str
    example_steps: list[LessonStepOut]
    common_error: str | None = None


class LeccionIndiceOut(BaseModel):
    """Una lección en el índice público.

    Sin el cuerpo de la lección a propósito: el índice solo necesita nombrarlas
    y enlazarlas, y son 17 filas que se piden en cada build del sitemap y de la
    página índice.
    """

    node_code: str
    node_name: str
    subject: str
    axis: str
    #: El eje ya escrito para mostrar ("Álgebra y Funciones").
    axis_label: str
