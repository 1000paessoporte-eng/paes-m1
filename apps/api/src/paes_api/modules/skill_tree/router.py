from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.skill_tree.models import SkillNode
from paes_api.modules.skill_tree.schemas import SkillNodeOut

router = APIRouter(prefix="/skill-tree", tags=["skill-tree"])


@router.get("", response_model=list[SkillNodeOut])
def list_skill_nodes(db: Session = Depends(get_db)) -> list[SkillNodeOut]:
    nodes = db.execute(select(SkillNode).order_by(SkillNode.axis, SkillNode.display_order))
    return [
        SkillNodeOut(
            **SkillNodeOut.model_validate(n).model_dump(exclude={"prerequisite_codes"}),
            prerequisite_codes=[p.code for p in n.prerequisites],
        )
        for (n,) in nodes.all()
    ]


@router.get("/{code}", response_model=SkillNodeOut)
def get_skill_node(code: str, db: Session = Depends(get_db)) -> SkillNodeOut:
    node = db.execute(select(SkillNode).where(SkillNode.code == code)).scalar_one_or_none()
    if node is None:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return SkillNodeOut(
        **SkillNodeOut.model_validate(node).model_dump(exclude={"prerequisite_codes"}),
        prerequisite_codes=[p.code for p in node.prerequisites],
    )
