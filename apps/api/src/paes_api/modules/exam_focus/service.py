"""Lógica del Modo Examen Focus.

Simplificación consciente para este MVP: el set de preguntas de un
intento no se persiste en una tabla propia (attempt_questions); en su
lugar se deriva de forma DETERMINÍSTICA (todas las preguntas activas,
ordenadas por skill_node_id/id), así que un GET posterior (resume tras
refresh) siempre reconstruye el mismo set sin necesitar tablas nuevas.
Cuando exista selección adaptativa real, esto se reemplaza por una
tabla de asignación explícita."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from paes_api.modules.content.models import Alternative, Question
from paes_api.modules.exam_focus.models import AttemptStatus, ExamAnswer, ExamAttempt
from paes_api.modules.exam_focus.schemas import (
    ExamAnswerIn,
    ExamAnswerState,
    ExamResultOut,
)
from paes_api.modules.users.models import User


def get_exam_questions(db: Session) -> list[Question]:
    stmt = (
        select(Question)
        .options(selectinload(Question.alternatives))
        .order_by(Question.skill_node_id, Question.id)
    )
    return list(db.execute(stmt).scalars().all())


def start_attempt(db: Session, user: User) -> ExamAttempt:
    attempt = ExamAttempt(user_id=user.id)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_attempt(db: Session, attempt_id: int) -> ExamAttempt | None:
    return db.get(ExamAttempt, attempt_id)


def get_answers_map(db: Session, attempt_id: int) -> dict[int, ExamAnswerState]:
    rows = db.execute(
        select(ExamAnswer).where(ExamAnswer.attempt_id == attempt_id)
    ).scalars()
    return {
        r.question_id: ExamAnswerState(
            selected_alternative_id=r.selected_alternative_id,
            time_spent_ms=r.time_spent_ms,
        )
        for r in rows
    }


def upsert_answer(db: Session, attempt_id: int, payload: ExamAnswerIn) -> None:
    existing = db.execute(
        select(ExamAnswer).where(
            ExamAnswer.attempt_id == attempt_id,
            ExamAnswer.question_id == payload.question_id,
        )
    ).scalar_one_or_none()
    now = datetime.now(UTC)
    if existing is not None:
        existing.selected_alternative_id = payload.selected_alternative_id
        existing.time_spent_ms = payload.time_spent_ms
        existing.answered_at = now
    else:
        db.add(
            ExamAnswer(
                attempt_id=attempt_id,
                question_id=payload.question_id,
                selected_alternative_id=payload.selected_alternative_id,
                time_spent_ms=payload.time_spent_ms,
                answered_at=now,
            )
        )
    db.commit()


def submit_attempt(db: Session, attempt: ExamAttempt) -> ExamResultOut:
    if attempt.status == AttemptStatus.IN_PROGRESS:
        attempt.status = AttemptStatus.SUBMITTED
        attempt.finished_at = datetime.now(UTC)
        db.commit()
        db.refresh(attempt)

    answers = get_answers_map(db, attempt.id)
    total = len(get_exam_questions(db))

    selected_ids = [a.selected_alternative_id for a in answers.values() if a.selected_alternative_id]
    correct = 0
    if selected_ids:
        correct = len(
            db.execute(
                select(Alternative).where(
                    Alternative.id.in_(selected_ids), Alternative.is_correct.is_(True)
                )
            )
            .scalars()
            .all()
        )

    finished_at = attempt.finished_at or datetime.now(UTC)
    elapsed = int((finished_at - attempt.started_at).total_seconds())

    return ExamResultOut(
        attempt_id=attempt.id,
        status=attempt.status,
        total_questions=total,
        answered=len(answers),
        correct=correct,
        elapsed_seconds=elapsed,
    )
