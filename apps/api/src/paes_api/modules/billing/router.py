from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.modules.billing import service
from paes_api.modules.billing.schemas import CanjearIn, MiPlanOut
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User

router = APIRouter(prefix="/plan", tags=["plan"])


def _armar(db: Session, user_id: int) -> MiPlanOut:
    plan, sub = service.plan_actual(db, user_id)
    limites = service.LIMITES[plan]
    return MiPlanOut(
        plan=plan,
        vence_el=sub.expires_at if sub else None,
        ensayos_usados=service.ensayos_del_mes(db, user_id),
        ensayos_limite=limites.ensayos_por_mes,
        carreras_limite=limites.carreras_en_meta,
        analisis_avanzado=limites.analisis_avanzado,
        limites_activos=service.LIMITES_ACTIVOS,
    )


@router.get("", response_model=MiPlanOut)
def mi_plan(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> MiPlanOut:
    return _armar(db, user.id)


@router.post("/canjear", response_model=MiPlanOut)
def canjear(
    payload: CanjearIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MiPlanOut:
    """Canjea un código promocional. El motivo del rechazo se le dice al
    estudiante tal cual: "ya venció" y "ya se agotó" son cosas distintas y
    esconderlo detrás de un error genérico solo genera correos a soporte."""
    try:
        service.canjear_codigo(db, user.id, payload.codigo)
    except service.CodigoInvalido as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _armar(db, user.id)
