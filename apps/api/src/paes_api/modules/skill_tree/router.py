from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.skill_tree import service
from paes_api.modules.skill_tree.schemas import SkillNodeProgressOut
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/skill-tree", tags=["skill-tree"])


@router.get("", response_model=list[SkillNodeProgressOut])
def list_skill_nodes(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[SkillNodeProgressOut]:
    return service.get_user_skill_tree(db, user.id)


@router.get("/recommended", response_model=SkillNodeProgressOut | None)
def get_recommended_node(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> SkillNodeProgressOut | None:
    return service.get_recommended_node(db, user.id)


@router.get("/{code}", response_model=SkillNodeProgressOut)
def get_skill_node(
    code: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> SkillNodeProgressOut:
    tree = service.get_user_skill_tree(db, user.id)
    node = next((n for n in tree if n.code == code), None)
    if node is None:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return node
