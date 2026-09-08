from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.core.email import diagnostico as diagnostico_email
from paes_api.modules.admin import service
from paes_api.modules.admin.schemas import AdminMetricsOut
from paes_api.modules.users.deps import get_current_admin
from paes_api.modules.users.models import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/metrics", response_model=AdminMetricsOut)
def metrics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> AdminMetricsOut:
    """Todo el panel en una sola llamada: son consultas agregadas y baratas, y
    partirlas en cinco endpoints solo multiplicaría los viajes."""
    return service.build_metrics(db)


@router.get("/correo")
def diagnostico_correo(
    _: User = Depends(get_current_admin),
) -> dict[str, object]:
    """¿El correo sale de verdad, o solo queda en el log?

    Existe porque sin SMTP configurado el envío NO falla: deja el mensaje en el
    log y sigue como si nada. Eso significa que se puede desplegar, probar y no
    ver ningún error mientras la recuperación de contraseña lleva semanas sin
    llegarle a nadie.

    `core/email.py` ya traía esta comprobación escrita --incluso abre la
    conexión y hace login, porque que las variables estén puestas no significa
    que sirvan-- pero ningún endpoint la exponía: estaba ahí sin que nadie
    pudiera llamarla. Esto la conecta.

    Nunca devuelve la contraseña del SMTP; sí dice si está puesta.
    """
    return diagnostico_email()
