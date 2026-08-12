from pydantic import BaseModel, ConfigDict

from paes_api.modules.content.models import Difficulty


class AlternativeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str
    text: str
    is_correct: bool
    distractor_justification: str | None = None


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    skill_node_id: int
    difficulty: Difficulty
    stem: str
    image_url: str | None = None
    alternatives: list[AlternativeOut]


class AlternativeSafeOut(BaseModel):
    """Alternativa sin is_correct ni distractor_justification — para
    listados públicos/autenticados que no deben revelar la respuesta."""

    id: int
    label: str
    text: str


class QuestionSafeOut(BaseModel):
    id: int
    skill_node_id: int
    difficulty: Difficulty
    stem: str
    image_url: str | None = None
    alternatives: list[AlternativeSafeOut]
