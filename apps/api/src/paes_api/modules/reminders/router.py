from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.database import get_db
from paes_api.modules.reminders import service

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/run")
def correr_recordatorios(
    x_cron_secret: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    """Manda los recordatorios del día. La llama el cron, no una persona.

    Va protegido por un secreto compartido y no por sesión: quien la ejecuta es
    una tarea programada, no un usuario. Sin el secreto configurado el endpoint
    queda cerrado —404— en vez de abierto: un disparador de correos masivos
    accesible por internet es exactamente la clase de puerta que no se deja
    entornada por comodidad.
    """
    secreto = get_settings().cron_secret
    if not secreto:
        raise HTTPException(status_code=404, detail="No encontrado")
    if x_cron_secret != secreto:
        raise HTTPException(status_code=401, detail="No autorizado")
    return service.enviar_recordatorios(db)
