from datetime import datetime

from pydantic import BaseModel

from paes_api.modules.content.models import Difficulty
from paes_api.modules.exam_focus.models import AttemptStatus


class ExamAlternativeOut(BaseModel):
    """Alternativa durante el examen: SIN is_correct ni
    distractor_justification. Esos datos solo se exponen después de
    submit (feature de Smart Feedback / autopsia del error)."""

    id: int
    label: str
    text: str


class ExamQuestionOut(BaseModel):
    id: int
    skill_node_id: int
    difficulty: Difficulty
    stem: str
    image_url: str | None = None
    alternatives: list[ExamAlternativeOut]


class ExamAnswerState(BaseModel):
    selected_alternative_id: int | None = None
    time_spent_ms: int = 0


class ExamStartOut(BaseModel):
    attempt_id: int
    started_at: datetime
    duration_limit_seconds: int
    questions: list[ExamQuestionOut]


class ExamStateOut(ExamStartOut):
    status: AttemptStatus
    answers: dict[int, ExamAnswerState]


class ExamAnswerIn(BaseModel):
    question_id: int
    selected_alternative_id: int | None = None
    time_spent_ms: int = 0


class ExamResultOut(BaseModel):
    attempt_id: int
    status: AttemptStatus
    total_questions: int
    answered: int
    correct: int
    elapsed_seconds: int


class ExamAttemptSummary(BaseModel):
    attempt_id: int
    started_at: datetime
    finished_at: datetime | None = None
    status: AttemptStatus
    total_questions: int
    answered: int
    correct: int


class ReviewAlternativeOut(BaseModel):
    """Alternativa en la revisión post-examen: SÍ incluye is_correct y
    distractor_justification — la autopsia del error."""

    id: int
    label: str
    text: str
    is_correct: bool
    distractor_justification: str | None = None
    selected: bool


class ReviewQuestionOut(BaseModel):
    id: int
    stem: str
    difficulty: Difficulty
    skill_node_id: int
    skill_node_code: str
    skill_node_name: str
    time_spent_ms: int
    answered_correctly: bool | None
    alternatives: list[ReviewAlternativeOut]


class NodeDiagnosisOut(BaseModel):
    skill_node_id: int
    skill_node_code: str
    skill_node_name: str
    axis: str
    total: int
    correct: int
    accuracy: float


class ExamReviewOut(BaseModel):
    attempt_id: int
    status: AttemptStatus
    questions: list[ReviewQuestionOut]
    node_diagnosis: list[NodeDiagnosisOut]
