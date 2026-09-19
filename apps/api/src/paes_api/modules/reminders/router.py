import hmac

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.database import get_db
from paes_api.modules.reminders import resumen, service

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
    todos los días desde que se creó. Resultado: cero recordatorios
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
    _exigir_secreto(authorization, x_cron_secret)
    return service.enviar_recordatorios(db)


@router.get("/resumen")
@router.post("/resumen")
def correr_resumen_semanal(
    authorization: str = Header(default=""),
    x_cron_secret: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    """Manda el resumen semanal de progreso. La llama el cron de los domingos,
    con el mismo secreto y las mismas reglas de acceso que `/run`."""
    _exigir_secreto(authorization, x_cron_secret)
    return resumen.enviar_resumenes(db)


def _exigir_secreto(authorization: str, x_cron_secret: str) -> None:
    secreto = get_settings().cron_secret
    if not secreto:
        raise HTTPException(status_code=404, detail="No encontrado")

    portador = authorization.removeprefix("Bearer ").strip()
    if not (
        hmac.compare_digest(portador, secreto) or hmac.compare_digest(x_cron_secret, secreto)
    ):
        raise HTTPException(status_code=401, detail="No autorizado")
