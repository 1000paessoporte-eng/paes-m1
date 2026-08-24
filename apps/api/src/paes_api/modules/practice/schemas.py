from pydantic import BaseModel

from paes_api.modules.content.models import Difficulty


class PracticeAlternativeOut(BaseModel):
    id: int
    label: str
    text: str


class PracticeQuestionOut(BaseModel):
    id: int
    difficulty: Difficulty
    stem: str
    image_url: str | None = None
    alternatives: list[PracticeAlternativeOut]


class PracticeStartOut(BaseModel):
    node_code: str
    node_name: str
    #: Si el nodo tiene teoría escrita. Al terminar una ronda floja la pantalla
    #: manda a leerla, y sin este dato el enlace apuntaría a un 404 en los nodos
    #: que todavía no la tienen.
    has_lesson: bool = False
    questions: list[PracticeQuestionOut]


class PracticeAnswerIn(BaseModel):
    question_id: int
    selected_alternative_id: int


class PracticeAnswerOut(BaseModel):
    is_correct: bool
    correct_alternative_id: int
    #: Desarrollo de por qué la respuesta correcta lo es.
    explanation: str | None = None
    #: El error que lleva justo a la alternativa marcada ("Dividió el total
    #: entre 6 en lugar de entre las 5 personas"). Va solo cuando se falló:
    #: en la correcta no hay distractor que justificar.
    #:
    #: Practicar un nodo es el momento en que alguien está trabajando su
    #: error a propósito, y era el único de los tres —demo, ensayo y
    #: práctica— que no lo devolvía.
    distractor_justification: str | None = None
    node_accuracy: float
    node_attempts: int
    newly_unlocked: list[str] = []
