"""Qué plan tiene cada usuario, qué puede hacer con él, y cómo se canjea un código.

Una decisión que ordena todo el módulo: **los límites del plan Gratis existen
en el código pero no se aplican todavía** (ver `limites_activos()`). Cortarle los
ensayos a alguien hoy sería mandarlo a una pantalla que dice "contrata Pro" y
que abajo dice "disponible pronto": la frustración sin la salida. El día que
exista la pasarela se cambia una constante y el sistema entero empieza a
respetarlos.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.modules.billing import flow
from paes_api.modules.billing.models import (
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
    """Cancela la renovación, sin quitar lo ya pagado. False si no había nada.

    Cancelar NO es cortar el acceso: el alumno pagó un período y ese período se
    respeta entero. Lo que se apaga es la renovación. Cortarle el acceso el día
    que cancela sería cobrarle por días que después no puede usar.

    Existía solo como "escríbenos a hola@": pedir un correo para dejar de pagar,
    cuando pagar son dos clics, es una fricción puesta a propósito y no algo que
    este producto quiera hacer.
    """
    suscripcion = db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .where(Subscription.status == SubscriptionStatus.ACTIVE)
        .order_by(Subscription.started_at.desc())
    ).scalars().first()

    if suscripcion is None:
        return False

    suscripcion.status = SubscriptionStatus.CANCELED
    db.commit()
    return True
