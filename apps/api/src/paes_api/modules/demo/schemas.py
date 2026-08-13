from pydantic import BaseModel

from paes_api.modules.content.models import Difficulty


class DemoAlternativeOut(BaseModel):
    """Sin is_correct: misma regla de integridad que el Modo Examen."""

    id: int
    label: str
    text: str


class DemoQuestionOut(BaseModel):
    id: int
    difficulty: Difficulty
    stem: str
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


class DemoGradeOut(BaseModel):
    items: list[DemoGradeItemOut]
    correct: int
    total: int
