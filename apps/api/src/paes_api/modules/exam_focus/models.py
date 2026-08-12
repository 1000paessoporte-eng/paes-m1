from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from paes_api.shared.base import Base

if TYPE_CHECKING:
    from paes_api.modules.users.models import User

EXAM_DURATION_SECONDS = 2 * 3600 + 20 * 60  # 2h 20m, duración oficial PAES M1


class AttemptStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    ABANDONED = "abandoned"


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_limit_seconds: Mapped[int] = mapped_column(
        Integer, default=EXAM_DURATION_SECONDS
    )
    status: Mapped[AttemptStatus] = mapped_column(
        Enum(AttemptStatus), default=AttemptStatus.IN_PROGRESS
    )

    user: Mapped["User"] = relationship(back_populates="exam_attempts")
    answers: Mapped[list["ExamAnswer"]] = relationship(back_populates="attempt")


class ExamAnswer(Base):
    """Tracking silencioso: time_spent_ms mide ritmo/fatiga por pregunta."""

    __tablename__ = "exam_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("exam_attempts.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    selected_alternative_id: Mapped[int | None] = mapped_column(
        ForeignKey("alternatives.id"), nullable=True
    )
    time_spent_ms: Mapped[int] = mapped_column(Integer, default=0)
    answered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    attempt: Mapped["ExamAttempt"] = relationship(back_populates="answers")
