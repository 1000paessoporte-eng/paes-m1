from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.content.models import Question
from paes_api.modules.content.schemas import QuestionSafeOut
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/questions", tags=["content"])


@router.get("", response_model=list[QuestionSafeOut])
def list_questions(
    skill_node_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Question]:
    """Nunca expone is_correct ni distractor_justification (ver
    QuestionSafeOut) — misma regla de integridad que el Modo Examen."""
    stmt = select(Question)
    if skill_node_id is not None:
        stmt = stmt.where(Question.skill_node_id == skill_node_id)
    return list(db.execute(stmt).scalars().all())
