import random

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.modules.content.models import Difficulty, Question
from paes_api.modules.demo.schemas import (
    DemoAlternativeOut,
    DemoGradeIn,
    DemoGradeItemOut,
    DemoGradeOut,
    DemoPassageOut,
    DemoQuestionOut,
)
from paes_api.modules.exam_focus.service import AXIS_LABELS, SUBJECT_INCLUDES
from paes_api.modules.skill_tree.models import SkillNode, Subject

router = APIRouter(prefix="/demo", tags=["demo"])

#: Cuántas preguntas trae la demo pública. Chico a propósito: es una
#: probada rápida sin cuenta, no un ensayo real (para eso hay que registrarse).
DEMO_QUESTION_COUNT = 5


@router.get("/questions", response_model=list[DemoQuestionOut])
@limiter.limit("20/minute")
def get_demo_questions(
    request: Request,
    subject: Subject = Query(default=Subject.M1),
    db: Session = Depends(get_db),
) -> list[DemoQuestionOut]:
    """Preguntas de prueba SIN cuenta: pública, sin auth, sin persistir nada.

    Solo fácil/medio -- la demo busca enganchar, no frustrar en el primer
    contacto con la plataforma.

    El sorteo se acota a la prueba pedida (`subject`). Antes salía de TODO el
    banco: quien entraba a "probar M1" podía recibir una pregunta de Historia,
    y la pantalla igual le decía "Competencia Matemática M1".
    """
    included = SUBJECT_INCLUDES[subject]
    questions = list(
        db.execute(
            select(Question)
            .join(Question.skill_node)
            .where(
                SkillNode.subject.in_(included),
                Question.difficulty.in_([Difficulty.FACIL, Difficulty.MEDIO]),
            )
            .options(
                selectinload(Question.alternatives),
                selectinload(Question.skill_node),
                selectinload(Question.passage),
            )
        )
        .scalars()
        .all()
    )
    sample = random.sample(questions, k=min(DEMO_QUESTION_COUNT, len(questions)))
    random.shuffle(sample)
    return [_a_salida(q) for q in sample]


def _a_salida(question: Question) -> DemoQuestionOut:
    """Aplana el nodo del árbol sobre la pregunta.

    El eje y el nombre del nodo viajan con cada pregunta para que la pantalla
    de resultado pueda decir en qué tema se falló sin una segunda llamada.
    """
    return DemoQuestionOut(
        id=question.id,
        difficulty=question.difficulty,
        stem=question.stem,
        subject=question.skill_node.subject,
        axis=question.skill_node.axis,
        axis_label=AXIS_LABELS.get(
            question.skill_node.axis.value, question.skill_node.axis.value
        ),
        node_name=question.skill_node.name,
        node_code=question.skill_node.code,
        passage=(
            DemoPassageOut(
                id=question.passage.id,
                title=question.passage.title,
                body=question.passage.body,
                kind=question.passage.kind,
                source_note=question.passage.source_note,
            )
            if question.passage is not None
            else None
        ),
        alternatives=[
            DemoAlternativeOut(id=a.id, label=a.label, text=a.text)
            for a in question.alternatives
        ],
    )


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
