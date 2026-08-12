from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.exam_focus import service
from paes_api.modules.exam_focus.models import AttemptStatus
from paes_api.modules.exam_focus.schemas import (
    ExamAnswerIn,
    ExamAttemptSummary,
    ExamQuestionOut,
    ExamResultOut,
    ExamReviewOut,
    ExamStartOut,
    ExamStateOut,
)
from paes_api.modules.users.service import get_or_create_demo_user

router = APIRouter(prefix="/exam", tags=["exam-focus"])


def _to_question_out(questions) -> list[ExamQuestionOut]:
    return [
        ExamQuestionOut(
            id=q.id,
            skill_node_id=q.skill_node_id,
            difficulty=q.difficulty,
            stem=q.stem,
            image_url=q.image_url,
            alternatives=[
                {"id": a.id, "label": a.label, "text": a.text} for a in q.alternatives
            ],
        )
        for q in questions
    ]


def _get_attempt_or_404(db: Session, attempt_id: int):
    attempt = service.get_attempt(db, attempt_id)
    if attempt is None:
        raise HTTPException(status_code=404, detail="Intento de examen no encontrado")
    return attempt


@router.get("", response_model=list[ExamAttemptSummary])
def list_exam_attempts(db: Session = Depends(get_db)) -> list[ExamAttemptSummary]:
    user = get_or_create_demo_user(db)
    return service.list_attempts(db, user)


@router.post("/start", response_model=ExamStartOut)
def start_exam(db: Session = Depends(get_db)) -> ExamStartOut:
    user = get_or_create_demo_user(db)
    attempt = service.start_attempt(db, user)
    questions = service.get_exam_questions(db)
    return ExamStartOut(
        attempt_id=attempt.id,
        started_at=attempt.started_at,
        duration_limit_seconds=attempt.duration_limit_seconds,
        questions=_to_question_out(questions),
    )


@router.get("/{attempt_id}", response_model=ExamStateOut)
def get_exam_state(attempt_id: int, db: Session = Depends(get_db)) -> ExamStateOut:
    attempt = _get_attempt_or_404(db, attempt_id)
    questions = service.get_exam_questions(db)
    answers = service.get_answers_map(db, attempt_id)
    return ExamStateOut(
        attempt_id=attempt.id,
        started_at=attempt.started_at,
        duration_limit_seconds=attempt.duration_limit_seconds,
        status=attempt.status,
        questions=_to_question_out(questions),
        answers=answers,
    )


@router.post("/{attempt_id}/answer")
def answer_question(
    attempt_id: int, payload: ExamAnswerIn, db: Session = Depends(get_db)
) -> dict[str, bool]:
    attempt = _get_attempt_or_404(db, attempt_id)
    if attempt.status != AttemptStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="El intento ya fue finalizado")
    service.upsert_answer(db, attempt_id, payload)
    return {"ok": True}


@router.post("/{attempt_id}/submit", response_model=ExamResultOut)
def submit_exam(attempt_id: int, db: Session = Depends(get_db)) -> ExamResultOut:
    attempt = _get_attempt_or_404(db, attempt_id)
    return service.submit_attempt(db, attempt)


@router.get("/{attempt_id}/review", response_model=ExamReviewOut)
def get_exam_review(attempt_id: int, db: Session = Depends(get_db)) -> ExamReviewOut:
    attempt = _get_attempt_or_404(db, attempt_id)
    if attempt.status != AttemptStatus.SUBMITTED:
        raise HTTPException(
            status_code=409, detail="La revisión solo está disponible tras finalizar el examen"
        )
    return service.get_review(db, attempt)
