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
