"""Qué plan tiene cada usuario, qué puede hacer con él, y cómo se canjea un código.

Una decisión que ordena todo el módulo: **los límites del plan Gratis existen
en el código pero no se aplican todavía** (ver `limites_activos()`). Cortarle los
ensayos a alguien hoy sería mandarlo a una pantalla que dice "contrata Pro" y
que abajo dice "disponible pronto": la frustración sin la salida. El día que
exista la pasarela se cambia una constante y el sistema entero empieza a
respetarlos.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.modules.billing import flow
from paes_api.modules.billing.models import (
    FlowCustomer,
    Origen,
    Pago,
    PagoStatus,
    Plan,
    PromoCode,
    Subscription,
    SubscriptionStatus,
)
from paes_api.modules.exam_focus.models import ExamAttempt
from paes_api.modules.users.models import User

logger = logging.getLogger(__name__)


def limites_activos() -> bool:
    """Si los límites del plan Gratis bloquean de verdad.

    En False se calculan y se muestran —el alumno ve "2 de 4 ensayos este
    mes"— pero no impiden nada. Se lee del entorno en cada llamada y no de una
    constante de módulo para que encenderlos sea cambiar una variable, no
    editar código y volver a desplegar.
    """
    return get_settings().limites_activos


@dataclass(frozen=True)
class Limites:
    """Lo que cada plan permite. `None` es sin límite.

    Solo entra acá lo que ALGUIEN aplica de verdad. Hubo un tercer campo,
    `analisis_avanzado`, que se declaraba, se informaba en la respuesta de
    /api/plan y no cerraba nada: el alumno del plan Gratis veía la analítica
    completa mientras la API le decía que no la tenía. Un límite que nadie
    comprueba no es un límite, es una promesa falsa en las dos direcciones.
    """

    ensayos_por_mes: int | None
    carreras_en_meta: int


def limites_de(plan: Plan) -> Limites:
    """Qué permite cada plan.

    El plan Gratis tiene que dejar APRENDER completo: las lecciones y el árbol
    entero están incluidos a propósito. Lo que se limita es el volumen de
    simulacros, que es lo caro de producir, no el acceso al contenido. Un muro
    sobre el material de estudio ahuyenta al que todavía no sabe si el producto
    le sirve; uno sobre la cantidad de ensayos lo deja comprobarlo y aprieta
    recién cuando ya le encontró el valor.

    La cuota del plan Gratis se lee del entorno en cada llamada para poder
    ajustarla mirando la conversión, sin desplegar.
    """
    if plan is Plan.GRATIS:
        return Limites(
            ensayos_por_mes=get_settings().ensayos_gratis_por_mes,
            carreras_en_meta=1,
        )
    return Limites(ensayos_por_mes=None, carreras_en_meta=10)





@dataclass(frozen=True)
class Producto:
    """Lo que se puede comprar.

    El precio vive ACÁ y no en el navegador. El cliente elige un identificador
    de producto; cuánto cuesta lo decide el servidor. Si el monto viajara desde
    el frontend, cualquiera podría comprar la temporada completa por cien pesos
    editando la petición.
    """

    id: str
    plan: Plan
    dias: int
    monto: int
    asunto: str


#: Los dos planes que se pueden comprar.
#:
#: Antes había cuatro (3 días, semana, mes, año). Los dos cortos se quitaron:
#: preparar la PAES no es algo que se haga en tres días, así que vendían una
#: promesa que el producto no puede cumplir, y de paso convertían la decisión
#: de compra en una comparación de cuatro columnas justo en el momento en que
#: hay que decidir una sola cosa.
#:
#: La regla que ordena la escala: a MENOR plazo, MAYOR precio por día. Quien
#: paga mes a mes conserva la libertad de irse; quien paga el año entrega el
#: efectivo por adelantado y recibe descuento. Si el precio diario fuera parejo
#: nadie compraría el plan largo.
#:
#: El anual no cuesta doce meses porque el producto es ESTACIONAL: nadie
#: prepara la PAES un año entero, el ciclo real son ocho o nueve meses. Por eso
#: sale exactamente nueve mensualidades (9 x 9.990 = 89.910, redondeado a
#: 89.900): se paga lo que se va a usar y los meses muertos no se cobran.
#:
#: Un test verifica que la escala se mantenga coherente si alguien cambia un
#: precio: ningún plan puede salir más barato por día que uno más largo.
PRODUCTOS: dict[str, Producto] = {
    "pro_mensual": Producto(
        id="pro_mensual",
        plan=Plan.PRO,
        dias=30,
        monto=9990,
        asunto="1000paes Pro - 1 mes",
    ),
    "pro_anual": Producto(
        id="pro_anual",
        plan=Plan.PRO,
        dias=365,
        monto=89900,
        asunto="1000paes Pro - 1 año",
    ),
}


class ProductoInvalido(Exception):
    """El identificador de producto no existe."""


class PagoNoEncontrado(Exception):
    """El token no corresponde a ninguna orden registrada."""


class MontoNoCoincide(Exception):
    """Flow informó un monto distinto del que se cobró al crear la orden."""


class CodigoInvalido(Exception):
    """El código no existe, venció, se agotó o ya lo usó esta persona."""


def _vigente(sub: Subscription, ahora: datetime) -> bool:
    if sub.status != SubscriptionStatus.ACTIVE:
        return False
    if sub.expires_at is None:
        return True
    vence = sub.expires_at
    if vence.tzinfo is None:
        vence = vence.replace(tzinfo=UTC)
    return vence > ahora


def plan_actual(db: Session, user_id: int) -> tuple[Plan, Subscription | None]:
    """El plan vigente del usuario. Sin suscripción activa, es Gratis.

    De paso marca como vencidas las suscripciones cuya fecha ya pasó: es el
    único lugar por el que pasan todas las consultas de plan, así que no hace
    falta un proceso aparte para eso.
    """
    ahora = datetime.now(UTC)
    subs = db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .where(Subscription.status == SubscriptionStatus.ACTIVE)
        .order_by(Subscription.started_at.desc())
    ).scalars().all()

    vigente: Subscription | None = None
    cambios = False
    for sub in subs:
        if not _vigente(sub, ahora) and sub.flow_subscription_id:
            # Se venció según lo que sabíamos, pero es recurrente: Flow pudo
            # haber cobrado el mes siguiente hace un minuto. Se le pregunta
            # ANTES de darla por terminada, porque acá no está la verdad.
            #
            # Esta consulta ocurre como mucho una vez por período y por
            # persona —solo en la ventana en que la fecha local ya pasó—, así
            # que no es un llamado a Flow en cada lectura de plan.
            try:
                sincronizar_con_flow(db, sub)
            except flow.FlowError as e:
                # Flow no contesta. NO se le corta el acceso a alguien que
                # probablemente está al día: se lo deja pasar y se reintenta
                # en la próxima lectura. El riesgo de regalar unas horas es
                # mucho menor que el de dejar afuera a quien pagó, y esto se
                # corrige solo apenas Flow vuelva a responder.
                logger.warning(
                    "no se pudo verificar la suscripción %s con Flow: %s",
                    sub.flow_subscription_id,
                    e,
                )
                if vigente is None:
                    vigente = sub
                continue

        if _vigente(sub, ahora):
            if vigente is None:
                vigente = sub
        else:
            sub.status = SubscriptionStatus.EXPIRED
            cambios = True
    if cambios:
        db.commit()

    if vigente is not None:
        return vigente.plan, vigente

    # Sin suscripción propia, el plan puede venir del colegio: eso es
    # exactamente lo que compra un establecimiento. Se devuelve sin
    # suscripción porque la suscripción no es de esta persona --el colegio
    # pagó por el curso-- y no hay nada que esta cuenta pueda cancelar.
    if _colegio_con_plan(db, user_id):
        return Plan.COLEGIOS, None

    return Plan.GRATIS, None


def _colegio_con_plan(db: Session, user_id: int) -> bool:
    """Si la persona pertenece a un curso con el plan al día."""
    from paes_api.modules.colegios.models import Colegio
    from paes_api.modules.users.models import User

    hasta = db.execute(
        select(Colegio.plan_hasta)
        .join(User, User.colegio_id == Colegio.id)
        .where(User.id == user_id)
    ).scalar_one_or_none()
    return hasta is not None and hasta >= datetime.now(UTC).date()


def ensayos_del_mes(db: Session, user_id: int) -> int:
    """Ensayos empezados desde el primer día del mes en curso.

    Se cuentan los empezados y no los terminados a propósito: si contara solo
    los terminados, abandonar un ensayo a la mitad sería la forma de saltarse
    el límite.
    """
    ahora = datetime.now(UTC)
    desde = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return db.execute(
        select(func.count(ExamAttempt.id))
        .where(ExamAttempt.user_id == user_id)
        .where(ExamAttempt.started_at >= desde)
    ).scalar_one()


def puede_rendir(db: Session, user_id: int) -> tuple[bool, str | None]:
    """Si puede empezar otro ensayo, y si no, por qué."""
    plan, _ = plan_actual(db, user_id)
    limite = limites_de(plan).ensayos_por_mes
    if limite is None:
        return True, None

    usados = ensayos_del_mes(db, user_id)
    if usados < limite:
        return True, None

    motivo = (
        f"Llegaste a los {limite} ensayos de este mes del plan Gratis. "
        "El plan Pro no tiene límite."
    )
    # Mientras no se pueda contratar Pro, el límite se informa pero no corta.
    return (not limites_activos()), motivo


def canjear_codigo(db: Session, user_id: int, codigo: str) -> Subscription:
    """Canjea un código y deja la suscripción creada.

    Cada condición se comprueba contra la base y no contra la confianza: un
    código sin tope real es una puerta abierta, y uno que se puede canjear dos
    veces desde la misma cuenta es un plan gratis infinito.
    """
    texto = codigo.strip().upper()
    promo = db.execute(
        select(PromoCode).where(PromoCode.codigo == texto)
    ).scalar_one_or_none()

    if promo is None or not promo.activo:
        raise CodigoInvalido("Ese código no existe o ya no está disponible.")

    ahora = datetime.now(UTC)
    if promo.vence_el is not None:
        vence = promo.vence_el
        if vence.tzinfo is None:
            vence = vence.replace(tzinfo=UTC)
        if vence < ahora:
            raise CodigoInvalido("Ese código ya venció.")

    if promo.usos >= promo.usos_maximos:
        raise CodigoInvalido("Ese código ya se agotó.")

    ya_usado = db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .where(Subscription.codigo == texto)
    ).scalar_one_or_none()
    if ya_usado is not None:
        raise CodigoInvalido("Ya canjeaste este código.")

    sub = Subscription(
        user_id=user_id,
        plan=promo.plan,
        origen=Origen.CODIGO,
        codigo=texto,
        expires_at=ahora + timedelta(days=promo.dias),
    )
    db.add(sub)
    promo.usos += 1
    db.commit()
    db.refresh(sub)
    return sub


# ---------------------------------------------------------------------------
# Cobro con Flow
# ---------------------------------------------------------------------------


def _nueva_orden(user_id: int) -> str:
    """Identificador de orden único y sin información sensible.

    Lleva el id del usuario para poder conciliar a ojo en el panel de Flow, y
    un sufijo aleatorio porque una persona puede intentar pagar varias veces y
    Flow exige que el commerceOrder no se repita nunca.
    """
    return f"p{user_id}-{uuid4().hex[:12]}"


def crear_pago(
    db: Session,
    user: User,
    producto_id: str,
    *,
    url_confirmacion: str,
    url_retorno: str,
) -> tuple[Pago, str]:
    """Registra la orden y la crea en Flow. Devuelve el pago y la URL de pago.

    El registro local se guarda ANTES de llamar a Flow. Si se hiciera al revés
    y la escritura fallara, existiría un cobro en Flow sin orden que lo respalde
    en la base: el usuario habría pagado y el sistema no tendría cómo saberlo.
    """
    producto = PRODUCTOS.get(producto_id)
    if producto is None:
        raise ProductoInvalido(producto_id)

    pago = Pago(
        user_id=user.id,
        orden=_nueva_orden(user.id),
        plan=producto.plan,
        dias=producto.dias,
        monto=producto.monto,
        status=PagoStatus.PENDIENTE,
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)

    datos = flow.crear_orden(
        orden=pago.orden,
        monto=producto.monto,
        asunto=producto.asunto,
        email=user.email,
        url_confirmacion=url_confirmacion,
        url_retorno=url_retorno,
    )
    pago.token = datos["token"]
    pago.flow_order = str(datos.get("flowOrder") or "")
    db.commit()

    return pago, f"{datos['url']}?token={datos['token']}"


def confirmar_pago(db: Session, token: str) -> Pago:
    """Confirma una orden consultando a Flow y activa la suscripción.

    Es el único camino por el que se otorga un plan pagado. Tres resguardos:

    1. **Se le pregunta a Flow.** El token que llega por el webhook no prueba
       nada por sí solo; el estado se obtiene de servidor a servidor.
    2. **Se compara el monto.** Si Flow informa menos de lo que la orden decía,
       no se activa nada y queda registrado para revisarlo a mano.
    3. **Es idempotente.** Flow puede llamar al webhook varias veces por la
       misma orden; una vez marcada como pagada, las llamadas siguientes no
       vuelven a extender la suscripción.
    """
    pago = db.execute(select(Pago).where(Pago.token == token)).scalar_one_or_none()
    if pago is None:
        raise PagoNoEncontrado(token)

    # Idempotencia: si ya se procesó, se devuelve tal cual sin tocar nada.
    if pago.status == PagoStatus.PAGADO:
        return pago

    datos = flow.estado(token)
    estado_flow = int(datos.get("status", 0))

    if estado_flow == flow.RECHAZADA:
        pago.status = PagoStatus.RECHAZADO
        db.commit()
        return pago
    if estado_flow == flow.ANULADA:
        pago.status = PagoStatus.ANULADO
        db.commit()
        return pago
    if estado_flow != flow.PAGADA:
        # Sigue pendiente: no se toca el registro. Flow volverá a avisar.
        return pago

    pagado = int(float(datos.get("amount", 0)))
    if pagado < pago.monto:
        # No se activa nada y no se marca como pagado: queda pendiente y visible
        # para revisión manual. Marcarlo como rechazado escondería el problema.
        raise MontoNoCoincide(
            f"orden {pago.orden}: se esperaban {pago.monto} y Flow informó {pagado}"
        )

    ahora = datetime.now(UTC)
    pago.status = PagoStatus.PAGADO
    pago.confirmado_at = ahora

    # La suscripción se ACUMULA sobre lo que quede vigente: quien renueva antes
    # de que se le venza no pierde los días que le sobraban.
    _, actual = plan_actual(db, pago.user_id)
    desde = actual.expires_at if actual and actual.expires_at else ahora
    db.add(
        Subscription(
            user_id=pago.user_id,
            plan=pago.plan,
            status=SubscriptionStatus.ACTIVE,
            origen=Origen.PAGO,
            started_at=ahora,
            expires_at=desde + timedelta(days=pago.dias),
        )
    )
    db.commit()
    db.refresh(pago)
    return pago


def cancelar_suscripcion(db: Session, user_id: int) -> bool:
    """Apaga la renovación sin quitar lo ya pagado. False si no había nada.

    Cancelar NO es cortar el acceso: el período cobrado se respeta entero.
    Cortarlo el día que alguien cancela es cobrarle días que después no puede
    usar, y es exactamente lo que hacía esta función hasta ahora: ponía
    `status = CANCELED`, y como `plan_actual` solo mira las ACTIVE, el plan
    volvía a Gratis en el acto. La pantalla prometía una cosa y el código hacía
    la contraria. Ahora se marca `cancelada_al_terminar` y la suscripción sigue
    ACTIVE hasta su fecha, momento en que vence sola como cualquier otra.

    Si la suscripción es recurrente, se cancela TAMBIÉN en Flow y eso ocurre
    primero: dejarla apagada solo de este lado significaría seguir cobrándole
    todos los meses a alguien que en su pantalla ve "cancelada".
    """
    suscripcion = db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .where(Subscription.status == SubscriptionStatus.ACTIVE)
        .order_by(Subscription.started_at.desc())
    ).scalars().first()

    if suscripcion is None:
        return False

    if suscripcion.flow_subscription_id:
        # Sin `at_period_end` Flow cortaría de inmediato. Lo que se apaga es la
        # renovación, no el mes en curso.
        flow.suscripcion_cancelar(suscripcion.flow_subscription_id, al_terminar=True)

    suscripcion.cancelada_al_terminar = True
    db.commit()
    return True


def cancelar_suscripciones_de_flow(db: Session, user_id: int) -> None:
    """Corta el cobro recurrente de una cuenta que se va a borrar.

    Va aparte de `cancelar_suscripcion` porque acá no importa respetar el
    período: la cuenta desaparece. Lo que no puede pasar bajo ninguna
    circunstancia es que quede una suscripción viva en Flow cobrándole todos
    los meses a una tarjeta cuyo dueño ya se fue y no tiene dónde entrar a
    reclamar.

    Los errores de Flow se propagan a propósito: borrar la cuenta y fallar en
    silencio al cancelar el cobro es el peor de los dos desenlaces posibles.
    """
    for sub in db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .where(Subscription.flow_subscription_id.is_not(None))
    ).scalars():
        flow.suscripcion_cancelar(sub.flow_subscription_id or "", al_terminar=False)


# ---------------------------------------------------------------------------
# Prueba gratis y cobro recurrente
# ---------------------------------------------------------------------------
#
# Cómo se sostiene la frase "3 días gratis, después $9.990 al mes, cancelas
# cuando quieras". Cada una de las tres partes es una pieza de código, porque
# una promesa de cobro que el sistema no cumple es publicidad engañosa y no un
# detalle de redacción:
#
#   "3 días gratis"      -> `trial_period_days` viaja a Flow en cada
#                           suscripción, con el mismo número que muestra la
#                           pantalla (`settings.trial_dias`).
#   "después $9.990"     -> el plan recurrente de Flow cobra solo. El monto es
#                           el del producto `pro_mensual`, no una constante
#                           aparte que pueda quedar desincronizada.
#   "cancelas cuando     -> `cancelar_suscripcion` apaga la renovación en Flow
#    quieras"              Y acá, y el acceso corre hasta el final del período
#                           que ya se cobró.
#
# La regla que ordena todo lo que sigue: **la fecha de término la manda Flow**.
# Este servicio no calcula cuándo vence una suscripción recurrente; se la
# pregunta a `subscription/get` y copia `period_end`. Quien cobra es quien sabe
# hasta cuándo está pagado, y cualquier aritmética local se desvía el primer
# día que Flow reintente un cobro o mueva la fecha de facturación.


#: El producto del que sale el precio del cobro recurrente. Es el mismo que se
#: vende suelto: si mañana el mensual sube, sube en un solo lugar.
PRODUCTO_RECURRENTE = "pro_mensual"


class TrialNoDisponible(Exception):
    """Falta configuración de Flow para el cobro recurrente."""


class TrialYaUsado(Exception):
    """Esta cuenta ya ocupó su prueba gratis."""


class YaTienePlan(Exception):
    """Ya tiene un plan vigente: no hay nada que probar."""


class TarjetaNoInscrita(Exception):
    """Flow no confirmó la inscripción de la tarjeta."""


class RegistroNoEncontrado(Exception):
    """El token de inscripción no corresponde a ningún cliente registrado."""


def trial_disponible() -> bool:
    """Si la prueba gratis se puede ofrecer.

    Exige credenciales de Flow *y* un plan recurrente creado en ese ambiente.
    Sin el plan, `subscription/create` falla y la persona vería el error
    después de haber entregado su tarjeta, que es la peor forma posible de
    descubrir que algo estaba mal configurado.
    """
    return flow.esta_configurado() and bool(get_settings().flow_plan_pro_id)


def trial_dias() -> int:
    return get_settings().trial_dias


def ya_uso_trial(db: Session, user_id: int) -> bool:
    """Si esta cuenta ya ocupó su prueba, aunque haya terminado hace meses.

    Se mira el historial completo y no solo lo vigente: el trial es uno por
    cuenta, y una suscripción vencida sigue siendo prueba de que se usó. Sin
    esto, cancelar y volver a suscribirse sería Pro gratis para siempre, en
    tandas de tres días.
    """
    return (
        db.execute(
            select(Subscription.id)
            .where(Subscription.user_id == user_id)
            .where(Subscription.origen == Origen.TRIAL)
            .limit(1)
        ).scalar_one_or_none()
        is not None
    )


def _fecha_flow(valor: object) -> datetime | None:
    """Convierte una fecha de Flow a datetime con zona horaria.

    Flow entrega "YYYY-MM-DD HH:MM:SS" y, en algunos campos, solo la fecha. Se
    aceptan las dos y también ISO con "T", porque el formato ha variado entre
    ambientes y una fecha mal leída acá termina en cortarle el acceso a alguien
    que pagó.
    """
    if not valor:
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def _cliente_flow(db: Session, user: User) -> FlowCustomer:
    """El cliente de Flow de esta persona, creándolo la primera vez.

    Se reutiliza siempre el mismo: un usuario con dos clientes en Flow es un
    usuario al que se le puede terminar cobrando dos veces, y eso no se
    descubre hasta que llega el reclamo.
    """
    cliente = db.execute(
        select(FlowCustomer).where(FlowCustomer.user_id == user.id)
    ).scalar_one_or_none()
    if cliente is not None:
        return cliente

    datos = flow.cliente_crear(
        nombre=(user.name or user.email).strip()[:80],
        email=user.email,
        externo=f"u{user.id}",
    )
    cliente = FlowCustomer(
        user_id=user.id,
        customer_id=str(datos["customerId"]),
        registrado=False,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def iniciar_trial(db: Session, user: User, *, url_retorno: str) -> str:
    """Deja lista la inscripción de la tarjeta y devuelve la URL de Flow.

    Acá NO se activa ningún plan: lo único que ocurre es que la persona queda
    encaminada al formulario donde Flow guarda su tarjeta. El trial se crea
    recién cuando Flow confirma esa inscripción de servidor a servidor, en
    `confirmar_tarjeta`. Activar algo en este paso sería regalarle Pro a quien
    abandone el formulario.
    """
    if not trial_disponible():
        raise TrialNoDisponible

    plan, _ = plan_actual(db, user.id)
    if plan is not Plan.GRATIS:
        raise YaTienePlan

    if ya_uso_trial(db, user.id):
        raise TrialYaUsado

    cliente = _cliente_flow(db, user)
    datos = flow.cliente_registrar(
        customer_id=cliente.customer_id, url_retorno=url_retorno
    )
    cliente.token_registro = str(datos["token"])
    db.commit()

    return f"{datos['url']}?token={datos['token']}"


def confirmar_tarjeta(db: Session, token: str) -> Subscription:
    """Verifica la tarjeta contra Flow, suscribe, y deja el trial activo.

    Es el único camino que activa la prueba. Igual que en el pago suelto, el
    token llega por el navegador y por sí solo no prueba nada: lo que vale es
    lo que Flow responde a `customer/getRegisterStatus`.

    Es idempotente: si la persona recarga la pantalla de vuelta, se le devuelve
    la suscripción que ya tiene en vez de crear una segunda en Flow, que sería
    cobrarle dos veces el mismo mes.
    """
    cliente = db.execute(
        select(FlowCustomer).where(FlowCustomer.token_registro == token)
    ).scalar_one_or_none()
    if cliente is None:
        raise RegistroNoEncontrado(token)

    existente = db.execute(
        select(Subscription)
        .where(Subscription.user_id == cliente.user_id)
        .where(Subscription.origen == Origen.TRIAL)
        .order_by(Subscription.started_at.desc())
    ).scalars().first()
    if existente is not None:
        return existente

    datos = flow.cliente_estado_registro(token)
    if not flow.tarjeta_quedo_inscrita(datos):
        raise TarjetaNoInscrita(str(datos.get("status", "")))

    cliente.registrado = True
    cliente.marca = str(datos.get("creditCardType") or "")[:40] or None
    ultimos = str(datos.get("last4CardDigits") or "")[-4:]
    cliente.ultimos4 = ultimos or None
    db.commit()

    dias = trial_dias()
    suscripcion = flow.suscripcion_crear(
        plan_id=get_settings().flow_plan_pro_id,
        customer_id=cliente.customer_id,
        trial_dias=dias,
    )

    ahora = datetime.now(UTC)
    # El período lo dice Flow. Si por algún motivo no viniera, se cae a los
    # días prometidos: más vale un trial que dura exactamente lo anunciado que
    # uno sin fecha de término.
    termina = (
        _fecha_flow(suscripcion.get("period_end"))
        or _fecha_flow(suscripcion.get("trial_end"))
        or ahora + timedelta(days=dias)
    )

    sub = Subscription(
        user_id=cliente.user_id,
        plan=Plan.PRO,
        status=SubscriptionStatus.ACTIVE,
        origen=Origen.TRIAL,
        started_at=ahora,
        expires_at=termina,
        flow_subscription_id=str(suscripcion["subscriptionId"]),
        en_trial=True,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def sincronizar_con_flow(db: Session, sub: Subscription) -> Subscription:
    """Copia desde Flow el estado real de una suscripción recurrente.

    Actualiza la fecha de término con `period_end` —hasta cuándo está
    efectivamente cobrado— y de paso registra si sigue en período de prueba y
    si la renovación quedó apagada desde el lado de Flow: alguien puede
    cancelar en el panel de la pasarela, no solo acá.

    Propaga `flow.FlowError` si Flow no responde. Quien llama decide qué hacer
    con eso; este módulo no inventa un estado cuando no lo sabe.
    """
    if not sub.flow_subscription_id:
        return sub

    datos = flow.suscripcion_estado(sub.flow_subscription_id)

    termina = _fecha_flow(datos.get("period_end"))
    if termina is not None:
        sub.expires_at = termina

    fin_trial = _fecha_flow(datos.get("trial_end"))
    sub.en_trial = fin_trial is not None and fin_trial > datetime.now(UTC)

    if str(datos.get("cancel_at_period_end", "0")).strip() in ("1", "true", "True"):
        sub.cancelada_al_terminar = True

    db.commit()
    db.refresh(sub)
    return sub


def sincronizar_todas(db: Session) -> int:
    """Reconcilia con Flow todas las suscripciones recurrentes vigentes.

    La reconciliación perezosa de `plan_actual` alcanza para que nadie pierda
    acceso, porque corre justo cuando la fecha local venció. Lo que no cubre es
    el caso inverso: alguien que dejó de pagar y no vuelve a entrar. Su
    suscripción queda ACTIVE en esta base para siempre, y las cifras internas
    —cuántos Pro hay— empiezan a contar gente que ya no paga.

    Por eso existe además este barrido diario, que es de dónde salen los
    números y no de dónde sale el acceso. Devuelve cuántas revisó.
    """
    subs = db.execute(
        select(Subscription)
        .where(Subscription.status == SubscriptionStatus.ACTIVE)
        .where(Subscription.flow_subscription_id.is_not(None))
    ).scalars().all()

    confirmadas: list[Subscription] = []
    for sub in subs:
        try:
            sincronizar_con_flow(db, sub)
            confirmadas.append(sub)
        except flow.FlowError as e:
            # Una suscripción que Flow no puede informar no detiene el barrido:
            # las demás sí se pueden reconciliar y esto vuelve a correr mañana.
            logger.warning(
                "no se pudo reconciliar la suscripción %s: %s",
                sub.flow_subscription_id,
                e,
            )

    # Solo se dan por vencidas las que Flow ALCANZÓ A CONFIRMAR. Marcar como
    # vencida una suscripción cuya consulta falló sería dejar sin plan a quien
    # está al día porque la pasarela no contestó, y con la misma política que
    # aplica `plan_actual`: cuando no se sabe, no se corta.
    ahora = datetime.now(UTC)
    for sub in confirmadas:
        if not _vigente(sub, ahora):
            sub.status = SubscriptionStatus.EXPIRED
    db.commit()
    return len(confirmadas)
