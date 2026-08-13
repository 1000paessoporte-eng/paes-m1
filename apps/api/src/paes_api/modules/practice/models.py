from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from paes_api.shared.base import Base


class PracticeAnswer(Base):
    """Registro de cada respuesta en Modo Práctica, para que Analítica pueda
    contarlas junto a las de Modo Ensayo (antes solo se acumulaba un contador
    agregado en UserSkillProgress, sin fecha, así que no entraban a la racha
    ni a las estadísticas diarias)."""

    __tablename__ = "practice_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    skill_node_id: Mapped[int] = mapped_column(ForeignKey("skill_nodes.id"), index=True)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
