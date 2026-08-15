from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.goals import service
from paes_api.modules.goals.models import Carrera, MetaUsuario
from paes_api.modules.goals.schemas import CarreraOut, MetaIn, MetaOut
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/carreras", response_model=list[CarreraOut])
def buscar_carreras(
    q: str = Query(min_length=3, description="Nombre de carrera o universidad"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Carrera]:
    return service.buscar_carreras(db, q)


@router.get("", response_model=MetaOut | None)
def ver_meta(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> MetaOut | None:
    return service.calcular_meta(db, user.id)


@router.put("", response_model=MetaOut)
def fijar_meta(
    payload: MetaIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MetaOut:
    carrera = db.get(Carrera, payload.carrera_id)
    if carrera is None:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")

    meta = db.execute(
        select(MetaUsuario).where(MetaUsuario.user_id == user.id)
    ).scalar_one_or_none()
    if meta is None:
        meta = MetaUsuario(user_id=user.id)
        db.add(meta)

    meta.carrera_id = carrera.id
    meta.puntaje_nem = payload.puntaje_nem
    meta.puntaje_ranking = payload.puntaje_ranking
    db.commit()

    resultado = service.calcular_meta(db, user.id)
    assert resultado is not None  # se acaba de crear
    return resultado


@router.delete("", status_code=204)
def borrar_meta(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> None:
    meta = db.execute(
        select(MetaUsuario).where(MetaUsuario.user_id == user.id)
    ).scalar_one_or_none()
    if meta is not None:
        db.delete(meta)
        db.commit()
