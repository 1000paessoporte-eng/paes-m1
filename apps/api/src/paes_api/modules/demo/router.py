import random

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.modules.content.models import Difficulty, Question
from paes_api.modules.demo.schemas import (
    DemoGradeIn,
    DemoGradeItemOut,
    DemoGradeOut,
    DemoQuestionOut,
)

router = APIRouter(prefix="/demo", tags=["demo"])

#: Cuántas preguntas trae la demo pública. Chico a propósito: es una
#: probada rápida sin cuenta, no un ensayo real (para eso hay que registrarse).
DEMO_QUESTION_COUNT = 5


@router.get("/questions", response_model=list[DemoQuestionOut])
@limiter.limit("20/minute")
def get_demo_questions(request: Request, db: Session = Depends(get_db)) -> list[Question]:
    """Preguntas de prueba SIN cuenta: pública, sin auth, sin persistir nada.
    Solo fácil/medio -- la demo busca enganchar, no frustrar en el primer
    contacto con la plataforma."""
    questions = list(
        db.execute(
            select(Question)
            .where(Question.difficulty.in_([Difficulty.FACIL, Difficulty.MEDIO]))
            .options(selectinload(Question.alternatives))
        )
        .scalars()
        .all()
    )
    sample = random.sample(questions, k=min(DEMO_QUESTION_COUNT, len(questions)))
    random.shuffle(sample)
    return sample


@router.post("/grade", response_model=DemoGradeOut)
@limiter.limit("20/minute")
def grade_demo(request: Request, payload: DemoGradeIn, db: Session = Depends(get_db)) -> DemoGradeOut:
    """Corrige la demo al vuelo, sin guardar ningún intento -- no hay usuario
    todavía, así que no hay dónde guardarlo."""
    question_ids = [a.question_id for a in payload.answers]
    if not question_ids:
        raise HTTPException(status_code=422, detail="No enviaste ninguna respuesta")

    questions = {
        q.id: q
        for q in db.execute(
            select(Question)
            .where(Question.id.in_(question_ids))
            .options(selectinload(Question.alternatives))
        )
        .scalars()
        .all()
    }

    items: list[DemoGradeItemOut] = []
    correct_count = 0
    for answer in payload.answers:
        question = questions.get(answer.question_id)
        if question is None:
            raise HTTPException(status_code=404, detail="Pregunta no encontrada")
        correct_alt = next(a for a in question.alternatives if a.is_correct)
        is_correct = answer.selected_alternative_id == correct_alt.id
        correct_count += int(is_correct)
        items.append(
            DemoGradeItemOut(
                question_id=question.id,
                is_correct=is_correct,
                correct_alternative_id=correct_alt.id,
                explanation=question.explanation,
            )
        )

    return DemoGradeOut(items=items, correct=correct_count, total=len(items))
