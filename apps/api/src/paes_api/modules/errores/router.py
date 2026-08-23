from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.modules.errores.models import ErrorCliente
from paes_api.modules.errores.schemas import ErrorClienteIn, ErrorClienteOut
from paes_api.modules.metrics.user_agent import clasificar
from paes_api.modules.users.deps import get_current_admin, get_current_user_optional
from paes_api.modules.users.models import User

router = APIRouter(prefix="/errores", tags=["errores"])

#: Cuántos errores distintos devuelve el panel. Más que esto no se revisa.
LIMITE_PANEL = 50

#: Ventana que mira el panel. Un error de hace un mes ya no dice nada del
#: estado actual del producto.
DIAS_PANEL = 14


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
def registrar_error(
    request: Request,
    payload: ErrorClienteIn,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
) -> None:
    """Guarda un error del navegador. Público: la mayoría revienta antes de
    que haya sesión, y de esos justamente no nos enterábamos nunca.

    NUNCA falla hacia el usuario: reportar que algo se rompió no puede ser lo
    segundo que se rompe. Y está limitado por IP porque un error en bucle
    dispara un reporte por cuadro.
    """
    ruta = payload.ruta.split("?")[0].split("#")[0][:255]
    if not ruta.startswith("/"):
        ruta = "/"

    _, _, navegador = clasificar(request.headers.get("user-agent"))
    mensaje = payload.mensaje.strip()[:500]

    # El mismo error en la misma ruta suma en vez de crear filas nuevas: un
    # bucle de render llenaría la tabla con miles de copias idénticas y taparía
    # todo lo demás.
    existente = db.execute(
        select(ErrorCliente).where(
            ErrorCliente.mensaje == mensaje,
            ErrorCliente.ruta == ruta,
            ErrorCliente.user_id == (user.id if user else None),
            ErrorCliente.ocurrido_en > datetime.now(UTC) - timedelta(hours=1),
        )
    ).scalars().first()

    if existente is not None:
        existente.veces += 1
    else:
        db.add(
            ErrorCliente(
                user_id=user.id if user else None,
                mensaje=mensaje,
                ruta=ruta,
                pila=payload.pila[:4000] if payload.pila else None,
                navegador=navegador,
            )
        )
    db.commit()


@router.get("", response_model=list[ErrorClienteOut])
def listar_errores(
    db: Session = Depends(get_db), _: User = Depends(get_current_admin)
) -> list[ErrorClienteOut]:
    """Los errores de las últimas dos semanas, el más repetido primero.

    Se agrupan por mensaje y ruta: lo que hay que arreglar es el error, no cada
    una de sus apariciones. Y se cuenta a cuántas CUENTAS distintas les pasó,
    que es lo que separa un caso raro de algo que hay que soltar todo y mirar.
    """
    desde = datetime.now(UTC) - timedelta(days=DIAS_PANEL)
    filas = db.execute(
        select(
            ErrorCliente.mensaje,
            ErrorCliente.ruta,
            func.max(ErrorCliente.pila).label("pila"),
            func.max(ErrorCliente.navegador).label("navegador"),
            func.sum(ErrorCliente.veces).label("veces"),
            func.max(ErrorCliente.ocurrido_en).label("ocurrido_en"),
            func.count(func.distinct(ErrorCliente.user_id)).label("usuarios"),
        )
        .where(ErrorCliente.ocurrido_en > desde)
        .group_by(ErrorCliente.mensaje, ErrorCliente.ruta)
        .order_by(func.sum(ErrorCliente.veces).desc())
        .limit(LIMITE_PANEL)
    ).all()

    return [
        ErrorClienteOut(
            mensaje=f.mensaje,
            ruta=f.ruta,
            pila=f.pila,
            navegador=f.navegador,
            veces=int(f.veces or 0),
            ocurrido_en=f.ocurrido_en,
            usuarios=int(f.usuarios or 0),
        )
        for f in filas
    ]
