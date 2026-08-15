from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.billing import service as billing
from paes_api.modules.content.models import Question
from paes_api.modules.exam_focus import service
from paes_api.modules.exam_focus.models import AttemptStatus
from paes_api.modules.exam_focus.schemas import (
    ExamAnswerIn,
    ExamAttemptSummary,
    ExamConfigIn,
    ExamOptionsOut,
    ExamQuestionOut,
    ExamResultOut,
    ExamReviewOut,
    ExamStartOut,
    ExamStateOut,
    PassageOut,
    RepasoOut,
)
from paes_api.modules.skill_tree.models import Subject
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/exam", tags=["exam-focus"])


def _to_question_out(questions: list[Question]) -> list[ExamQuestionOut]:
    return [
        ExamQuestionOut(
            id=q.id,
            skill_node_id=q.skill_node_id,
            skill_node_name=q.skill_node.name if q.skill_node else "",
            axis=(
                service.AXIS_LABELS.get(q.skill_node.axis.value, "")
                if q.skill_node
                else ""
            ),
            difficulty=q.difficulty,
            stem=q.stem,
            image_url=q.image_url,
            passage=(
                PassageOut(
                    id=q.passage.id,
                    title=q.passage.title,
                    body=q.passage.body,
                    kind=q.passage.kind,
                    source_note=q.passage.source_note,
                )
                if q.passage
                else None
            ),
            alternatives=[
                {"id": a.id, "label": a.label, "text": a.text} for a in q.alternatives
            ],
        )
        for q in questions
    ]


def _get_attempt_or_404(db: Session, attempt_id: int, user: User):
    attempt = service.get_attempt(db, attempt_id)
    if attempt is None or attempt.user_id != user.id:
        raise HTTPException(status_code=404, detail="Intento de examen no encontrado")
    return attempt


@router.get("/options", response_model=ExamOptionsOut)
def get_exam_options(
    subject: Subject = Subject.M1, db: Session = Depends(get_db)
) -> ExamOptionsOut:
    """Ejes y disponibilidad del banco, para la pantalla de configuración."""
    return service.get_options(db, subject)


@router.get("/repaso", response_model=RepasoOut)
def get_repaso(
    subject: Subject = Subject.M1,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> RepasoOut:
    """Sugerencia para el botón "Ensayo de repaso" en la config del ensayo."""
    return service.get_repaso(db, user.id, subject)


@router.get("", response_model=list[ExamAttemptSummary])
def list_exam_attempts(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[ExamAttemptSummary]:
    return service.list_attempts(db, user)


@router.post("/start", response_model=ExamStartOut)
def start_exam(
    config: ExamConfigIn | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ExamStartOut:
    # El plan Gratis tiene un tope de ensayos al mes. Hoy se informa y no
    # bloquea (ver billing.LIMITES_ACTIVOS): cortarle el paso a alguien
    # mandándolo a contratar un plan que todavía no se puede contratar es
    # frustración sin salida.
    permitido, motivo = billing.puede_rendir(db, user.id)
    if not permitido:
        raise HTTPException(status_code=409, detail=motivo)

    attempt = service.start_attempt(db, user, config or ExamConfigIn())
    questions = service.attempt_questions(db, attempt)
    if not questions:
        raise HTTPException(
            status_code=409,
            detail="No hay preguntas disponibles con los ejes seleccionados",
        )
    return ExamStartOut(
        attempt_id=attempt.id,
        started_at=attempt.started_at,
        duration_limit_seconds=attempt.duration_limit_seconds,
        config=service.attempt_config(attempt, len(questions)),
        questions=_to_question_out(questions),
    )


@router.get("/{attempt_id}", response_model=ExamStateOut)
def get_exam_state(
    attempt_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ExamStateOut:
    attempt = _get_attempt_or_404(db, attempt_id, user)
    questions = service.attempt_questions(db, attempt)
    answers = service.get_answers_map(db, attempt_id)
    return ExamStateOut(
        attempt_id=attempt.id,
        started_at=attempt.started_at,
        duration_limit_seconds=attempt.duration_limit_seconds,
        status=attempt.status,
        config=service.attempt_config(attempt, len(questions)),
        questions=_to_question_out(questions),
        answers=answers,
    )


@router.post("/{attempt_id}/answer")
def answer_question(
    attempt_id: int,
    payload: ExamAnswerIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, bool]:
    attempt = _get_attempt_or_404(db, attempt_id, user)
    if attempt.status != AttemptStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="El intento ya fue finalizado")
    service.upsert_answer(db, attempt_id, payload)
    return {"ok": True}


@router.post("/{attempt_id}/submit", response_model=ExamResultOut)
def submit_exam(
    attempt_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ExamResultOut:
    attempt = _get_attempt_or_404(db, attempt_id, user)
    return service.submit_attempt(db, attempt)


@router.get("/{attempt_id}/result", response_model=ExamResultOut)
def get_exam_result(
    attempt_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ExamResultOut:
    """Mismo resumen que devuelve submit, para volver a abrir un ensayo pasado."""
    attempt = _get_attempt_or_404(db, attempt_id, user)
    if attempt.status != AttemptStatus.SUBMITTED:
        raise HTTPException(
            status_code=409, detail="El ensayo todavía no ha sido finalizado"
        )
    return service.submit_attempt(db, attempt)


@router.delete("/{attempt_id}", status_code=204)
def delete_exam_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    attempt = _get_attempt_or_404(db, attempt_id, user)
    service.delete_attempt(db, attempt)
    return Response(status_code=204)


@router.get("/{attempt_id}/review", response_model=ExamReviewOut)
def get_exam_review(
    attempt_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ExamReviewOut:
    attempt = _get_attempt_or_404(db, attempt_id, user)
    if attempt.status != AttemptStatus.SUBMITTED:
        raise HTTPException(
            status_code=409,
            detail="La revisión solo está disponible tras finalizar el ensayo",
        )
    return service.get_review(db, attempt)
