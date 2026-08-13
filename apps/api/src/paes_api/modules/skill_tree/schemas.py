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


class SkillNodeProgressOut(SkillNodeOut):
    status: ProgressStatus
    accuracy: float
    attempts: int
