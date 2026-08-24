import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from paes_api.core.database import get_db
from paes_api.modules.content.models import Question
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.practice.schemas import (
    PracticeAlternativeOut,
    PracticeAnswerIn,
    PracticeAnswerOut,
    PracticeQuestionOut,
    PracticeStartOut,
)
from paes_api.modules.skill_tree import service as skill_tree_service
from paes_api.modules.skill_tree.models import SkillNode
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/practice", tags=["practice"])


def _get_node_or_404(db: Session, code: str) -> SkillNode:
    """El nodo que se va a practicar, esté desbloqueado o no.

    El árbol RECOMIENDA un orden; dejó de imponerlo. Un nodo bloqueado se
    sigue dibujando gris y diciendo qué conviene dominar antes, pero ya no
    prohíbe entrar.

    El 403 que había acá dejaba las cinco pruebas en pie salvo M2, cuyos
    dieciséis nodos cuelgan todos de un tema de M1: el alumno que iba a rendir
    M2 abría su árbol, veía dieciséis tarjetas grises y no podía practicar ni
    una de las 207 preguntas de esa prueba. Y era incoherente con el propio
    producto, porque Modo Ensayo nunca bloqueó nada: ese mismo alumno podía
    rendir un ensayo de M2 completo el primer día.
    """
    node = db.execute(select(SkillNode).where(SkillNode.code == code)).scalar_one_or_none()
    if node is None:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return node


@router.get("/{code}/questions", response_model=PracticeStartOut)
def get_practice_questions(
    code: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> PracticeStartOut:
    node = _get_node_or_404(db, code)
    questions = list(
        db.execute(
            select(Question)
            .where(Question.skill_node_id == node.id)
            .options(selectinload(Question.alternatives))
        )
        .scalars()
        .all()
    )
    # Sin barajar, la sesion de practica repite siempre la misma secuencia
    # (util para "practicar de nuevo" tipo repeticion espaciada solo si el
    # orden cambia entre sesiones).
    random.shuffle(questions)
    return PracticeStartOut(
        node_code=node.code,
        node_name=node.name,
        has_lesson=node.lesson is not None,
        questions=[
            PracticeQuestionOut(
                id=q.id,
                difficulty=q.difficulty,
                stem=q.stem,
                image_url=q.image_url,
                alternatives=[
                    PracticeAlternativeOut(id=a.id, label=a.label, text=a.text)
                    for a in q.alternatives
                ],
            )
            for q in questions
        ],
    )


@router.post("/{code}/answer", response_model=PracticeAnswerOut)
def answer_practice_question(
    code: str,
    payload: PracticeAnswerIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PracticeAnswerOut:
    node = _get_node_or_404(db, code)
    question = db.execute(
        select(Question)
        .where(Question.id == payload.question_id)
        .options(selectinload(Question.alternatives))
    ).scalar_one_or_none()
    if question is None or question.skill_node_id != node.id:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada en este nodo")

    selected = next(
        (a for a in question.alternatives if a.id == payload.selected_alternative_id), None
    )
    if selected is None:
        raise HTTPException(status_code=422, detail="Alternativa inválida para esta pregunta")
    correct_alt = next(a for a in question.alternatives if a.is_correct)

    db.add(
        PracticeAnswer(
            user_id=user.id,
            question_id=question.id,
            skill_node_id=node.id,
            is_correct=selected.is_correct,
        )
    )

    newly_unlocked = skill_tree_service.apply_single_answer(
        db, user.id, node.id, selected.is_correct
    )

    tree = skill_tree_service.get_user_skill_tree(db, user.id)
    updated = next(n for n in tree if n.code == code)

    return PracticeAnswerOut(
        is_correct=selected.is_correct,
        correct_alternative_id=correct_alt.id,
        explanation=question.explanation,
        distractor_justification=(
            None if selected.is_correct else selected.distractor_justification
        ),
        node_accuracy=updated.accuracy,
        node_attempts=updated.attempts,
        newly_unlocked=[n.name for n in newly_unlocked],
    )
