from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.skill_tree import service
from paes_api.modules.skill_tree.models import Subject
from paes_api.modules.skill_tree.schemas import LessonOut, SkillNodeProgressOut
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/skill-tree", tags=["skill-tree"])


@router.get("", response_model=list[SkillNodeProgressOut])
def list_skill_nodes(
    subject: Subject = Query(
        default=Subject.M1,
        description="Prueba cuyo temario se quiere ver. El árbol es distinto "
        "por prueba: cada una tiene sus propios ejes y prerrequisitos.",
    ),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[SkillNodeProgressOut]:
    return service.get_user_skill_tree(db, user.id, subject=subject)


@router.get("/recommended", response_model=SkillNodeProgressOut | None)
def get_recommended_node(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> SkillNodeProgressOut | None:
    return service.get_recommended_node(db, user.id)


@router.get("/{code}/leccion", response_model=LessonOut)
def get_lesson(
    code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LessonOut:
    """La teoría del nodo. 404 si el nodo todavía no tiene lección escrita."""
    leccion = service.get_lesson(db, code)
    if leccion is None:
        raise HTTPException(status_code=404, detail="Este tema aún no tiene lección")
    return leccion


@router.get("/{code}", response_model=SkillNodeProgressOut)
def get_skill_node(
    code: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> SkillNodeProgressOut:
    tree = service.get_user_skill_tree(db, user.id)
    node = next((n for n in tree if n.code == code), None)
    if node is None:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return node
