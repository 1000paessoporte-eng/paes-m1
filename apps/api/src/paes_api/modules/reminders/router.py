from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.database import get_db
from paes_api.modules.reminders import service

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/run")
@router.post("/run")
def correr_recordatorios(
    authorization: str = Header(default=""),
    x_cron_secret: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    """Manda los recordatorios del día. La llama el cron, no una persona.

    ACEPTA GET, y ese es el arreglo. Los cron de Vercel disparan un GET con la
    cabecera `Authorization: Bearer $CRON_SECRET`; este endpoint solo aceptaba
    POST con una cabecera propia, así que la tarea programada respondía 405
    todos los días a las 22:00 desde que se creó. Resultado: cero recordatorios
    enviados en toda la vida del producto, con los siete usuarios teniéndolos
    activados y siendo este el único mecanismo de retención que existe.

    Se aceptan las dos formas --el Bearer de Vercel y la cabecera propia-- para
    poder dispararlo a mano desde una terminal sin depender del formato del
    proveedor.

    Va protegido por un secreto compartido y no por sesión: quien la ejecuta es
    una tarea programada, no un usuario. Sin el secreto configurado el endpoint
    queda cerrado --404-- en vez de abierto: un disparador de correos masivos
    accesible por internet es exactamente la clase de puerta que no se deja
    entornada por comodidad.
    """
    secreto = get_settings().cron_secret
    if not secreto:
        raise HTTPException(status_code=404, detail="No encontrado")

    portador = authorization.removeprefix("Bearer ").strip()
    if portador != secreto and x_cron_secret != secreto:
        raise HTTPException(status_code=401, detail="No autorizado")
    return service.enviar_recordatorios(db)
