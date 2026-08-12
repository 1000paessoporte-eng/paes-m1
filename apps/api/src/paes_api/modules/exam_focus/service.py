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
    ExamAttemptSummary,
    ExamResultOut,
    ExamReviewOut,
    NodeDiagnosisOut,
    ReviewAlternativeOut,
    ReviewQuestionOut,
)
from paes_api.modules.skill_tree import service as skill_tree_service
from paes_api.modules.skill_tree.models import SkillNode
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
        skill_tree_service.apply_attempt_results(db, attempt.user_id, attempt.id)

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


def _count_correct(db: Session, selected_ids: list[int]) -> int:
    if not selected_ids:
        return 0
    return len(
        db.execute(
            select(Alternative).where(
                Alternative.id.in_(selected_ids), Alternative.is_correct.is_(True)
            )
        )
        .scalars()
        .all()
    )


def list_attempts(db: Session, user: User) -> list[ExamAttemptSummary]:
    attempts = db.execute(
        select(ExamAttempt)
        .where(ExamAttempt.user_id == user.id)
        .order_by(ExamAttempt.started_at.desc())
    ).scalars()
    total = len(get_exam_questions(db))

    out = []
    for a in attempts:
        answers = get_answers_map(db, a.id)
        selected_ids = [x.selected_alternative_id for x in answers.values() if x.selected_alternative_id]
        out.append(
            ExamAttemptSummary(
                attempt_id=a.id,
                started_at=a.started_at,
                finished_at=a.finished_at,
                status=a.status,
                total_questions=total,
                answered=len(answers),
                correct=_count_correct(db, selected_ids),
            )
        )
    return out


def get_review(db: Session, attempt: ExamAttempt) -> ExamReviewOut:
    questions = get_exam_questions(db)
    answers = get_answers_map(db, attempt.id)

    node_ids = {q.skill_node_id for q in questions}
    nodes = db.execute(select(SkillNode).where(SkillNode.id.in_(node_ids))).scalars().all()
    node_by_id = {n.id: n for n in nodes}

    review_questions: list[ReviewQuestionOut] = []
    node_stats: dict[int, dict[str, int]] = {}

    for q in questions:
        ans = answers.get(q.id)
        selected_id = ans.selected_alternative_id if ans else None
        time_spent = ans.time_spent_ms if ans else 0
        correct_alt = next((a for a in q.alternatives if a.is_correct), None)

        answered_correctly = None
        if selected_id is not None:
            answered_correctly = correct_alt is not None and selected_id == correct_alt.id

        stats = node_stats.setdefault(q.skill_node_id, {"total": 0, "correct": 0})
        stats["total"] += 1
        if answered_correctly:
            stats["correct"] += 1

        node = node_by_id.get(q.skill_node_id)
        review_questions.append(
            ReviewQuestionOut(
                id=q.id,
                stem=q.stem,
                difficulty=q.difficulty,
                skill_node_id=q.skill_node_id,
                skill_node_code=node.code if node else "",
                skill_node_name=node.name if node else "",
                time_spent_ms=time_spent,
                answered_correctly=answered_correctly,
                alternatives=[
                    ReviewAlternativeOut(
                        id=a.id,
                        label=a.label,
                        text=a.text,
                        is_correct=a.is_correct,
                        distractor_justification=a.distractor_justification,
                        selected=(a.id == selected_id),
                    )
                    for a in q.alternatives
                ],
            )
        )

    node_diagnosis = [
        NodeDiagnosisOut(
            skill_node_id=nid,
            skill_node_code=node_by_id[nid].code,
            skill_node_name=node_by_id[nid].name,
            axis=node_by_id[nid].axis.value,
            total=s["total"],
            correct=s["correct"],
            accuracy=(s["correct"] / s["total"] if s["total"] else 0.0),
        )
        for nid, s in node_stats.items()
    ]
    node_diagnosis.sort(key=lambda d: d.accuracy)

    return ExamReviewOut(
        attempt_id=attempt.id,
        status=attempt.status,
        questions=review_questions,
        node_diagnosis=node_diagnosis,
    )
