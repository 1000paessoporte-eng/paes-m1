from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from paes_api.modules.skill_tree.models import Subject
from paes_api.shared.base import Base

if TYPE_CHECKING:
    from paes_api.modules.users.models import User

EXAM_DURATION_SECONDS = 2 * 3600 + 20 * 60  # 2h 20m, duración oficial PAES M1


class AttemptStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    ABANDONED = "abandoned"


class Pace(StrEnum):
    """Ritmo del ensayo: ajusta el tiempo respecto de la proporción oficial.

    El oficial replica la razón de la PAES real; los otros dos existen porque a
    veces conviene entrenar bajo presión o dedicar más tiempo a razonar cuando
    recién se está estudiando la materia.
    """

    OFICIAL = "oficial"
    EXIGENTE = "exigente"
    RELAJADO = "relajado"


#: Factor sobre la duración oficial para cada ritmo.
PACE_FACTOR: dict[Pace, float] = {
    Pace.OFICIAL: 1.0,
    Pace.EXIGENTE: 0.8,
    Pace.RELAJADO: 1.25,
}


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
    pace: Mapped[Pace] = mapped_column(Enum(Pace), default=Pace.OFICIAL)
    subject: Mapped[Subject] = mapped_column(
        Enum(Subject), default=Subject.M1, server_default=Subject.M1.name
    )
    #: Ejes elegidos separados por coma. NULL o vacío significa "todos".
    axes: Mapped[str | None] = mapped_column(String(200), nullable=True)
    #: Puntaje PAES estimado, calculado al finalizar. NULL mientras esté en curso.
    estimated_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship(back_populates="exam_attempts")
    answers: Mapped[list["ExamAnswer"]] = relationship(back_populates="attempt")
    questions: Mapped[list["ExamAttemptQuestion"]] = relationship(
        back_populates="attempt",
        order_by="ExamAttemptQuestion.position",
        cascade="all, delete-orphan",
    )


class ExamAttemptQuestion(Base):
    """Set de preguntas asignado a un intento, en su orden definitivo.

    Antes el set se derivaba determinísticamente (todas las preguntas activas),
    lo que servía mientras el examen fuera siempre completo. Con ensayos
    configurables (cantidad y ejes a elección) la selección es aleatoria, así
    que debe persistirse para que un GET posterior —resume tras refresh, o la
    revisión meses después— reconstruya exactamente el mismo ensayo.
    """

    __tablename__ = "exam_attempt_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("exam_attempts.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)

    attempt: Mapped["ExamAttempt"] = relationship(back_populates="questions")


class ExamAnswer(Base):
    """Tracking silencioso: time_spent_ms mide ritmo/fatiga por pregunta.

    Una pregunta tiene UNA respuesta dentro de un intento, y eso lo garantiza
    la base. Sin esa restricción, dos guardados simultáneos de la misma
    pregunta creaban dos filas: a partir de ahí el propio guardado reventaba al
    leerlas (`scalar_one_or_none` sobre dos filas), así que esa pregunta ya no
    se podía volver a responder en lo que quedaba del ensayo y terminaba
    contada como omitida.
    """

    __tablename__ = "exam_answers"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_exam_answer_intento_pregunta"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("exam_attempts.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    selected_alternative_id: Mapped[int | None] = mapped_column(
        ForeignKey("alternatives.id"), nullable=True
    )
    time_spent_ms: Mapped[int] = mapped_column(Integer, default=0)
    #: Marcada para revisar más tarde durante el ensayo.
    flagged: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    answered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    attempt: Mapped["ExamAttempt"] = relationship(back_populates="answers")
