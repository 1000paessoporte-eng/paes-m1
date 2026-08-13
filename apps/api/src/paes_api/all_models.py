"""Importa todos los modelos SQLAlchemy para registrarlos en Base.metadata
antes de que se resuelvan relaciones por nombre (string) o se comparen
metadatos (Alembic autogenerate, scripts de seed, tests de integración).

Cualquier módulo que necesite el registro completo de modelos debe hacer
`import paes_api.all_models` (por sus efectos secundarios) en lugar de
importar modelos individuales."""

from paes_api.modules.analytics.models import StudyStreak
from paes_api.modules.content.models import Alternative, Question
from paes_api.modules.exam_focus.models import (
    ExamAnswer,
    ExamAttempt,
    ExamAttemptQuestion,
)
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.skill_tree.models import SkillNode, UserSkillProgress
from paes_api.modules.users.models import PasswordResetToken, User

__all__ = [
    "Alternative",
    "ExamAnswer",
    "ExamAttempt",
    "ExamAttemptQuestion",
    "PasswordResetToken",
    "PracticeAnswer",
    "Question",
    "SkillNode",
    "StudyStreak",
    "User",
    "UserSkillProgress",
]
