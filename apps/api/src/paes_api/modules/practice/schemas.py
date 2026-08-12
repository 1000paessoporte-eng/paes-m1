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
    questions: list[PracticeQuestionOut]


class PracticeAnswerIn(BaseModel):
    question_id: int
    selected_alternative_id: int


class PracticeAnswerOut(BaseModel):
    is_correct: bool
    correct_alternative_id: int
    #: Desarrollo de por qué la respuesta correcta lo es.
    explanation: str | None = None
    node_accuracy: float
    node_attempts: int
    newly_unlocked: list[str] = []
