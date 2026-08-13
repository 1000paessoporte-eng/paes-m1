from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.modules.metrics.models import PageView
from paes_api.modules.metrics.schemas import PageViewIn
from paes_api.modules.users.deps import get_current_user_optional
from paes_api.modules.users.models import User

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/pageview", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("60/minute")
def registrar_visita(
    request: Request,
    payload: PageViewIn,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
) -> None:
    """Registra una visita. Público: la mayor parte del tráfico que interesa
    medir es de gente que todavía no tiene cuenta.

    Nunca falla hacia el usuario: medir no puede romper la navegación."""
    path = payload.path
    # Solo rutas internas, y sin query string: los parámetros pueden llevar el
    # token de restablecer contraseña, que no debe quedar guardado.
    if not path.startswith("/") or path.startswith("//"):
        return
    path = path.split("?")[0].split("#")[0][:255]

    db.add(
        PageView(
            path=path,
            visitor_id=payload.visitor_id,
            user_id=user.id if user else None,
        )
    )
    db.commit()
