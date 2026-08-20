from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.billing import service as billing
from paes_api.modules.goals import service
from paes_api.modules.goals.models import Carrera, MetaUsuario
from paes_api.modules.goals.schemas import (
    CarreraOut,
    MetaOut,
    NotasIn,
    OrdenIn,
    PostularIn,
)
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/carreras", response_model=list[CarreraOut])
def buscar_carreras(
    q: str = Query(min_length=3, description="Nombre de carrera, universidad o sede"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Carrera]:
    return service.buscar_carreras(db, q)


@router.get("", response_model=MetaOut)
def ver_meta(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> MetaOut:
    return service.calcular_meta(db, user.id)


@router.post("/postulaciones", response_model=MetaOut, status_code=201)
def agregar_postulacion(
    payload: PostularIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MetaOut:
    """Agrega una carrera al final de la lista de preferencias."""
    if db.get(Carrera, payload.carrera_id) is None:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")

    actuales = db.execute(
        select(MetaUsuario).where(MetaUsuario.user_id == user.id)
    ).scalars().all()

    if any(m.carrera_id == payload.carrera_id for m in actuales):
        raise HTTPException(status_code=409, detail="Esa carrera ya está en tu lista")

    # El tope de carreras es la diferencia entre Gratis y Pro que la página de
    # planes lleva anunciando desde siempre. Estaba definido en
    # `billing.limites_de()` y no lo aplicaba nadie: cualquiera podía agregar
    # diez. Cobrar por algo que ya se entrega gratis es la peor forma de
    # cobrar.
    plan_actual, _ = billing.plan_actual(db, user.id)
    tope = billing.limites_de(plan_actual).carreras_en_meta
    if len(actuales) >= tope:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Tu plan permite {tope} "
                + ("carrera" if tope == 1 else "carreras")
                + " en Mi meta. Con Pro puedes seguir hasta "
                + f"{service.MAX_PREFERENCIAS}."
            ),
        )

    db.add(
        MetaUsuario(
            user_id=user.id,
            carrera_id=payload.carrera_id,
            preferencia=len(actuales) + 1,
        )
    )
    db.commit()
    return service.calcular_meta(db, user.id)


@router.put("/orden", response_model=MetaOut)
def reordenar(
    payload: OrdenIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MetaOut:
    """Reordena la lista. El orden decide dónde queda uno, así que es parte
    de la decisión y no un detalle de presentación."""
    postulaciones = {
        m.carrera_id: m
        for m in db.execute(
            select(MetaUsuario).where(MetaUsuario.user_id == user.id)
        ).scalars().all()
    }
    for posicion, carrera_id in enumerate(payload.carrera_ids, start=1):
        meta = postulaciones.get(carrera_id)
        if meta is not None:
            meta.preferencia = posicion
    db.commit()
    return service.calcular_meta(db, user.id)


@router.delete("/postulaciones/{carrera_id}", response_model=MetaOut)
def quitar_postulacion(
    carrera_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MetaOut:
    meta = db.execute(
        select(MetaUsuario)
        .where(MetaUsuario.user_id == user.id)
        .where(MetaUsuario.carrera_id == carrera_id)
    ).scalar_one_or_none()
    if meta is not None:
        db.delete(meta)
        db.flush()
        # Las preferencias se renumeran: dejar un hueco (1, 2, 4) haría que la
        # lista dijera algo falso sobre el orden real.
        resto = db.execute(
            select(MetaUsuario)
            .where(MetaUsuario.user_id == user.id)
            .order_by(MetaUsuario.preferencia)
        ).scalars().all()
        for posicion, m in enumerate(resto, start=1):
            m.preferencia = posicion
        db.commit()
    return service.calcular_meta(db, user.id)


@router.put("/notas", response_model=MetaOut)
def guardar_notas(
    payload: NotasIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MetaOut:
    user.puntaje_nem = payload.puntaje_nem
    user.puntaje_ranking = payload.puntaje_ranking
    db.commit()
    return service.calcular_meta(db, user.id)
