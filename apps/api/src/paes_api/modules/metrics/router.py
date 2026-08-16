from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.modules.metrics.models import PageView
from paes_api.modules.metrics.schemas import PageViewIn
from paes_api.modules.metrics.user_agent import clasificar, es_robot
from paes_api.modules.users.deps import get_current_user_optional
from paes_api.modules.users.models import User

router = APIRouter(prefix="/metrics", tags=["metrics"])


def _host_de(referrer: str | None) -> str | None:
    """Solo el dominio de origen, nunca la URL completa.

    Para saber por qué canal llega la gente basta con "google.com". La ruta
    ajena, en cambio, puede traer términos de búsqueda, identificadores de
    campaña o datos de la sesión de otro sitio, y no hay ninguna razón para
    guardarlos.

    El tráfico interno se descarta: una visita que viene de otra página del
    propio sitio no es un canal de entrada, es navegación, y contarla como
    origen taparía a los canales de verdad.
    """
    if not referrer:
        return None
    try:
        host = urlparse(referrer).hostname
    except ValueError:
        return None
    if not host:
        return None
    host = host.removeprefix("www.").lower()
    if host.endswith("1000paes.cl") or "milpaes" in host or host == "localhost":
        return None
    return host[:120]


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

    # El user agent se lee y se descarta en el acto: a la base solo llegan las
    # tres categorías gruesas, nunca la cadena original.
    ua = request.headers.get("user-agent")
    device, sistema, navegador = clasificar(ua)

    db.add(
        PageView(
            path=path,
            visitor_id=payload.visitor_id,
            user_id=user.id if user else None,
            device=device,
            os=sistema,
            browser=navegador,
            referrer=_host_de(payload.referrer),
            es_bot=es_robot(ua),
        )
    )
    db.commit()
