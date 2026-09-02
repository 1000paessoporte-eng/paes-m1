import logging
import time
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    Form,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.database import get_db
from paes_api.modules.billing import flow, service
from paes_api.modules.billing.models import FlowCustomer
from paes_api.modules.billing.schemas import (
    CanjearIn,
    MiPlanOut,
    PagarIn,
    PagarOut,
    ProductoOut,
    ProductosOut,
    TrialOut,
)
from paes_api.modules.users.deps import get_current_admin, get_current_user
from paes_api.modules.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plan", tags=["plan"])


def _tarjeta(db: Session, user_id: int) -> str | None:
    """"Visa ····4242", o None si no hay tarjeta inscrita.

    Nunca sale de acá otra cosa: el número vive en Flow y este servidor no lo
    tiene ni puede tenerlo.
    """
    cliente = db.execute(
        select(FlowCustomer)
        .where(FlowCustomer.user_id == user_id)
        .where(FlowCustomer.registrado.is_(True))
    ).scalar_one_or_none()
    if cliente is None or not cliente.ultimos4:
        return None
    return f"{cliente.marca or 'Tarjeta'} ····{cliente.ultimos4}"


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
        en_trial=bool(sub and sub.en_trial),
        cancelada_al_terminar=bool(sub and sub.cancelada_al_terminar),
        # Se ofrece solo a quien puede tomarla de verdad: sin plan vigente y
        # sin haberla usado antes. Mostrarle "3 días gratis" a alguien que ya
        # los ocupó es prometerle algo que el siguiente clic le va a negar.
        trial_disponible=(
            service.trial_disponible()
            and plan is service.Plan.GRATIS
            and not service.ya_uso_trial(db, user_id)
        ),
        trial_dias=service.trial_dias(),
        trial_monto=service.PRODUCTOS[service.PRODUCTO_RECURRENTE].monto,
        tarjeta=_tarjeta(db, user_id),
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
        trial_disponible=service.trial_disponible(),
        trial_dias=service.trial_dias(),
        trial_monto=service.PRODUCTOS[service.PRODUCTO_RECURRENTE].monto,
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
        # El cobro recurrente necesita, ademas de las credenciales, un plan
        # creado en ESTE ambiente. Es el error de configuracion mas facil de
        # cometer --el plan del sandbox no existe en produccion-- y el mas
        # caro: se descubre cuando alguien ya entrego su tarjeta.
        "plan_recurrente": s.flow_plan_pro_id or "(sin configurar)",
        "trial_dias": s.trial_dias,
    }

    if not flow.esta_configurado():
        info["resultado"] = "faltan credenciales"
        return info

    if s.flow_plan_pro_id:
        try:
            plan = flow.plan_estado(s.flow_plan_pro_id)
            info["plan_en_flow"] = {
                clave: plan.get(clave)
                for clave in ("planId", "amount", "interval", "trial_period_days", "status")
                if clave in plan
            }
        except flow.FlowError as e:
            info["plan_en_flow"] = f"error: {e}"
    else:
        info["plan_en_flow"] = "sin FLOW_PLAN_PRO_ID: la prueba gratis esta apagada"

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


@router.post("/cancelar", response_model=MiPlanOut)
def cancelar(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> MiPlanOut:
    """Apaga la renovación de la suscripción activa.

    No corta el acceso: lo ya pagado se respeta hasta su fecha de término. Si
    no hay nada activo responde 409 en vez de fingir que hizo algo.
    """
    if not service.cancelar_suscripcion(db, user.id):
        raise HTTPException(status_code=409, detail="No tienes una suscripción activa")
    return _armar(db, user.id)


@router.post("/trial", response_model=TrialOut)
def iniciar_trial(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TrialOut:
    """Empieza la prueba gratis: devuelve la URL donde Flow pide la tarjeta.

    Este endpoint NO activa nada. Devuelve una dirección de Flow y hasta ahí
    llega su efecto; el plan se enciende recién cuando Flow confirma la
    inscripción en `/plan/trial/retorno`. La distinción es la misma que en el
    pago: si acá se activara el plan, tomarlo sin dejar tarjeta sería cuestión
    de llamar a esta URL.

    Cada motivo de rechazo se le dice a la persona tal cual, porque son cosas
    distintas y esconderlas tras un error genérico solo produce correos a
    soporte: no está disponible, ya la usaste, o ya tienes plan.
    """
    settings = get_settings()
    api_base = settings.api_url.rstrip("/")

    try:
        url = service.iniciar_trial(
            db,
            user,
            # Flow devuelve el navegador a la API y no al frontend a
            # propósito: la vuelta trae el token de inscripción y hay que
            # verificarlo de servidor a servidor antes de encender nada. La
            # API confirma y recién ahí redirige a la pantalla del alumno.
            url_retorno=f"{api_base}/api/plan/trial/retorno",
        )
    except service.TrialNoDisponible:
        raise HTTPException(
            status_code=503,
            detail="La prueba gratis todavía no está disponible.",
        ) from None
    except service.TrialYaUsado:
        raise HTTPException(
            status_code=409,
            detail="Ya ocupaste tu prueba gratis: es una por cuenta.",
        ) from None
    except service.YaTienePlan:
        raise HTTPException(
            status_code=409, detail="Ya tienes un plan activo."
        ) from None
    except flow.FlowNoConfigurado:
        raise HTTPException(
            status_code=503,
            detail="La prueba gratis todavía no está disponible.",
        ) from None
    except flow.FlowError as e:
        logger.error("Flow falló al inscribir la tarjeta: %s", e)
        raise HTTPException(
            status_code=502,
            detail="No se pudo iniciar la prueba. Inténtalo de nuevo en unos minutos.",
        ) from None

    return TrialOut(url=url)


@router.get("/trial/retorno")
@router.post("/trial/retorno")
async def retorno_trial(
    request: Request,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """A donde Flow devuelve el navegador tras el formulario de la tarjeta.

    Confirma de servidor a servidor y luego redirige a la pantalla del alumno.
    Es el único camino que activa la prueba.

    Acepta GET y POST porque Flow ha usado los dos según el ambiente, y el
    token puede venir en el cuerpo o en la query. Un retorno que responde 405
    deja a la persona con la tarjeta ya inscrita en Flow y sin plan acá: el
    peor estado posible de los dos lados.

    Nunca devuelve un error a la cara: pase lo que pase redirige a
    `/plan/resultado`, que lee el plan real y explica lo que corresponda. Una
    pantalla de error crudo de la API después de haber entregado una tarjeta es
    exactamente donde alguien concluye que le cobraron mal.
    """
    front = get_settings().frontend_url.rstrip("/")

    # El token se busca en la query y en el cuerpo, sin suponer cuál usó Flow.
    # Leer solo uno de los dos es la clase de detalle que funciona en sandbox y
    # falla en producción.
    recibido = (request.query_params.get("token") or "").strip()
    if not recibido:
        try:
            formulario = await request.form()
            recibido = str(formulario.get("token") or "").strip()
        except Exception:  # noqa: BLE001 -- un cuerpo ilegible no es un token
            recibido = ""

    destino = f"{front}/plan/resultado?origen=trial"
    if not recibido:
        return RedirectResponse(url=f"{destino}&estado=sin-token", status_code=303)

    try:
        service.confirmar_tarjeta(db, recibido)
    except service.RegistroNoEncontrado:
        logger.warning("retorno de inscripción con un token sin cliente asociado")
        destino = f"{destino}&estado=desconocido"
    except service.TarjetaNoInscrita as e:
        logger.info("la tarjeta no quedó inscrita en Flow: %s", e)
        destino = f"{destino}&estado=sin-tarjeta"
    except flow.FlowError as e:
        # La tarjeta puede haber quedado inscrita igual. No se le dice que
        # falló: se le manda a la pantalla que consulta el plan de verdad, y
        # el barrido diario reconcilia lo que haya quedado a medias.
        logger.error("Flow falló al confirmar la inscripción: %s", e)
        destino = f"{destino}&estado=pendiente"

    return RedirectResponse(url=destino, status_code=303)


@router.post("/flow/suscripcion", status_code=status.HTTP_200_OK)
def webhook_suscripcion(
    # El nombre del campo lo fija Flow; acá se recibe con alias para no
    # arrastrar camelCase al resto del archivo.
    subscription_id: str = Form(default="", alias="subscriptionId"),
    token: str = Form(default=""),
    db: Session = Depends(get_db),
) -> Response:
    """Aviso de Flow cuando cobra una cuota del plan recurrente.

    Adelanta la reconciliación de esa suscripción, pero **el sistema no depende
    de este aviso para estar correcto**, y eso es deliberado: el contenido
    exacto de esta notificación no está documentado por Flow, así que colgar de
    ella la fecha hasta la que alguien tiene acceso sería construir sobre algo
    que puede cambiar sin avisar.

    Las dos garantías reales están en otra parte: `plan_actual` le pregunta a
    Flow en cuanto la fecha local vence —así nadie que pagó pierde acceso— y el
    barrido diario reconcilia todo lo demás. Esto solo hace que el mes nuevo
    aparezca en pantalla enseguida en vez de en la próxima lectura.

    Responde 200 siempre salvo error interno: Flow reintenta ante cualquier
    otra cosa y reintentar una reconciliación no aporta nada, porque es
    idempotente por construcción.
    """
    identificador = subscription_id.strip()

    if not identificador and token.strip():
        # Algunas notificaciones traen el token del pago en vez del
        # identificador de la suscripción. Se le pregunta a Flow por ese pago a
        # ver si nombra la suscripción; si no la nombra, no se adivina.
        try:
            datos = flow.estado(token.strip())
            identificador = str(datos.get("subscriptionId") or "").strip()
        except flow.FlowError as e:
            logger.warning("no se pudo leer el pago avisado por Flow: %s", e)

    if not identificador:
        logger.info("aviso de suscripción sin identificador reconocible; se ignora")
        return Response(status_code=status.HTTP_200_OK)

    sub = db.execute(
        select(service.Subscription).where(
            service.Subscription.flow_subscription_id == identificador
        )
    ).scalars().first()
    if sub is None:
        logger.warning("Flow avisó de una suscripción que no está en la base")
        return Response(status_code=status.HTTP_200_OK)

    try:
        service.sincronizar_con_flow(db, sub)
    except flow.FlowError as e:
        logger.error("no se pudo reconciliar tras el aviso de Flow: %s", e)

    return Response(status_code=status.HTTP_200_OK)


@router.get("/flow/reconciliar")
@router.post("/flow/reconciliar")
def reconciliar(
    authorization: str = Header(default=""),
    x_cron_secret: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    """Barrido diario: pone al día todas las suscripciones recurrentes.

    Lo que la reconciliación perezosa de `plan_actual` no cubre es el caso de
    quien deja de pagar y no vuelve a entrar: su suscripción quedaría ACTIVE
    para siempre en esta base y las cifras internas contarían como Pro a gente
    que ya no lo es. Esto existe para eso, no para el acceso.

    Mismo esquema de autenticación que los recordatorios: secreto compartido,
    GET aceptado porque los cron de Vercel disparan GET con `Authorization:
    Bearer`, y 404 cuando el secreto no está configurado --una tarea que habla
    con la pasarela de pago no se deja abierta por comodidad.
    """
    secreto = get_settings().cron_secret
    if not secreto:
        raise HTTPException(status_code=404, detail="No encontrado")

    portador = authorization.removeprefix("Bearer ").strip()
    if portador != secreto and x_cron_secret != secreto:
        raise HTTPException(status_code=401, detail="No autorizado")

    return {"revisadas": service.sincronizar_todas(db)}
