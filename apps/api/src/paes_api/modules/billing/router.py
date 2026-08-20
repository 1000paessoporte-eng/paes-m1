import logging
import time
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Response, status
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.database import get_db
from paes_api.modules.billing import flow, service
from paes_api.modules.billing.schemas import (
    CanjearIn,
    MiPlanOut,
    PagarIn,
    PagarOut,
    ProductoOut,
    ProductosOut,
)
from paes_api.modules.users.deps import get_current_admin, get_current_user
from paes_api.modules.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plan", tags=["plan"])


def _armar(db: Session, user_id: int) -> MiPlanOut:
    plan, sub = service.plan_actual(db, user_id)
    limites = service.limites_de(plan)
    return MiPlanOut(
        plan=plan,
        vence_el=sub.expires_at if sub else None,
        ensayos_usados=service.ensayos_del_mes(db, user_id),
        ensayos_limite=limites.ensayos_por_mes,
        carreras_limite=limites.carreras_en_meta,
        limites_activos=service.limites_activos(),
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


@router.get("/productos", response_model=ProductosOut)
def productos() -> ProductosOut:
    """Qué se puede comprar y si el cobro está habilitado.

    Público: la página de precios lo consulta sin sesión para decidir si
    muestra el botón de pago o el aviso de "disponible pronto"."""
    return ProductosOut(
        pago_disponible=flow.esta_configurado(),
        productos=[
            ProductoOut(
                id=p.id,
                plan=p.plan.value,
                dias=p.dias,
                monto=p.monto,
                asunto=p.asunto,
            )
            for p in service.PRODUCTOS.values()
        ],
    )


@router.post("/pagar", response_model=PagarOut)
def pagar(
    payload: PagarIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PagarOut:
    """Crea la orden en Flow y devuelve la URL a la que hay que ir a pagar."""
    settings = get_settings()
    api_base = settings.api_url.rstrip("/")
    front = settings.frontend_url.rstrip("/")

    try:
        pago, url = service.crear_pago(
            db,
            user,
            payload.producto,
            # Flow llama a esta URL de servidor a servidor. Debe ser pública y
            # apuntar a la API, nunca al frontend.
            url_confirmacion=f"{api_base}/api/plan/flow/confirmar",
            url_retorno=f"{front}/plan/resultado",
        )
    except service.ProductoInvalido:
        raise HTTPException(status_code=422, detail="Ese plan no existe.") from None
    except flow.FlowNoConfigurado:
        raise HTTPException(
            status_code=503,
            detail="El pago en línea todavía no está disponible.",
        ) from None
    except flow.FlowError as e:
        logger.error("Flow falló al crear la orden: %s", e)
        raise HTTPException(
            status_code=502,
            detail="No se pudo iniciar el pago. Inténtalo de nuevo en unos minutos.",
        ) from None

    return PagarOut(url=url, orden=pago.orden)


@router.post("/flow/confirmar", status_code=status.HTTP_200_OK)
def confirmar(
    token: str = Form(...),
    db: Session = Depends(get_db),
) -> Response:
    """Webhook de Flow. Es el ÚNICO camino que activa una suscripción pagada.

    Deliberadamente público y sin autenticación: lo llama Flow, no un usuario.
    Su seguridad no está en quién lo llama sino en que el token recibido se
    verifica contra Flow de servidor a servidor antes de activar nada. Un token
    inventado no encuentra orden, y uno robado tampoco sirve: Flow dirá si esa
    orden está pagada y por cuánto.

    Responde 200 salvo error interno: Flow reintenta ante cualquier otra cosa, y
    reintentar una orden ya procesada no aporta nada porque la confirmación es
    idempotente."""
    try:
        service.confirmar_pago(db, token)
    except service.PagoNoEncontrado:
        # No se filtra que el token es desconocido: se responde 200 igual para
        # no convertir el webhook en un oráculo que confirme tokens válidos.
        logger.warning("Flow confirmó un token sin orden asociada")
    except service.MontoNoCoincide as e:
        # Nunca debería pasar. Si pasa, hay que mirarlo a mano: la orden queda
        # pendiente y sin suscripción otorgada.
        logger.error("Monto distinto del esperado: %s", e)
    except flow.FlowError as e:
        logger.error("No se pudo verificar el pago con Flow: %s", e)
        # 500 para que Flow reintente: puede haber sido una caída transitoria.
        raise HTTPException(status_code=500, detail="reintentar") from None

    return Response(status_code=status.HTTP_200_OK)


@router.get("/flow/diagnostico")
def diagnostico(user: User = Depends(get_current_admin)) -> dict[str, object]:
    """Qué responde Flow exactamente, para no diagnosticar a ciegas.

    Existe porque configurar una pasarela falla siempre por lo mismo —una
    credencial del ambiente equivocado, una URL mal escrita— y el mensaje que
    ve el usuario es deliberadamente genérico. Sin esto, la única forma de
    saber qué pasó es leer los logs del servidor.

    Solo para admin: la respuesta de Flow puede nombrar la cuenta y el estado
    del comercio. Nunca devuelve las credenciales; sí dice si están puestas y
    contra qué ambiente se está hablando, que es lo que hace falta para
    detectar el error más común: llaves de producción apuntando al sandbox.
    """
    s = get_settings()
    info: dict[str, object] = {
        "configurado": flow.esta_configurado(),
        "ambiente": s.flow_base_url,
        "api_url": s.api_url,
        # Solo el largo y el prefijo: suficiente para notar que quedó pegada a
        # medias o con espacios, sin exponer el valor.
        "api_key_largo": len(s.flow_api_key),
        "api_key_empieza": s.flow_api_key[:4] if s.flow_api_key else "",
        "secret_key_largo": len(s.flow_secret_key),
        "timeout_segundos": flow.TIMEOUT,
    }

    if not flow.esta_configurado():
        info["resultado"] = "faltan credenciales"
        return info

    inicio = time.monotonic()
    try:
        flow.crear_orden(
            orden=f"diag-{uuid4().hex[:10]}",
            monto=5990,
            asunto="Prueba de diagnóstico",
            # El correo del propio admin, no uno inventado: Flow valida que
            # exista y rechaza los de fantasía con el código 1620. Usar uno
            # falso hacía fallar el diagnóstico por un motivo que no tenía
            # nada que ver con lo que se estaba comprobando.
            email=user.email,
            url_confirmacion=f"{s.api_url.rstrip('/')}/api/plan/flow/confirmar",
            url_retorno=f"{s.frontend_url.rstrip('/')}/plan/resultado",
        )
    except flow.FlowError as e:
        info["resultado"] = "error"
        info["mensaje_de_flow"] = str(e)
        info["tardo_segundos"] = round(time.monotonic() - inicio, 1)
        return info

    info["resultado"] = "ok: Flow aceptó una orden de prueba"
    info["tardo_segundos"] = round(time.monotonic() - inicio, 1)
    return info
