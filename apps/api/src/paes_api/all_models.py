"""Importa todos los modelos SQLAlchemy para registrarlos en Base.metadata
antes de que se resuelvan relaciones por nombre (string) o se comparen
metadatos (Alembic autogenerate, scripts de seed, tests de integración).

Cualquier módulo que necesite el registro completo de modelos debe hacer
`import paes_api.all_models` (por sus efectos secundarios) en lugar de
importar modelos individuales."""

from paes_api.modules.analytics.models import StudyStreak
from paes_api.modules.billing.models import (
    FlowCustomer,
    Pago,
    PromoCode,
    Subscription,
)
from paes_api.modules.colegios.models import Colegio, EnsayoProgramado
from paes_api.modules.content.models import (
    Alternative,
    Lesson,
    Question,
    ReadingPassage,
)
from paes_api.modules.errores.models import ErrorCliente
from paes_api.modules.exam_focus.models import (
    ExamAnswer,
    ExamAttempt,
    ExamAttemptQuestion,
)
from paes_api.modules.goals.models import Carrera, MetaUsuario
from paes_api.modules.leads.models import Lead
from paes_api.modules.metrics.models import PageView
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.skill_tree.models import SkillNode, UserSkillProgress
from paes_api.modules.users.models import LoginEvent, PasswordResetToken, User

__all__ = [
    "Alternative",
    "Carrera",
    "Colegio",
    "EnsayoProgramado",
    "ErrorCliente",
    "ExamAnswer",
    "ExamAttempt",
    "ExamAttemptQuestion",
    "FlowCustomer",
    "Lead",
    "Lesson",
    "LoginEvent",
    "MetaUsuario",
    "PageView",
    "Pago",
    "PasswordResetToken",
    "PracticeAnswer",
    "PromoCode",
    "Question",
    "ReadingPassage",
    "SkillNode",
    "StudyStreak",
    "Subscription",
    "User",
    "UserSkillProgress",
]
