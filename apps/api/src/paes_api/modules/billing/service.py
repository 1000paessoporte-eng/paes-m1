"""Qué plan tiene cada usuario, qué puede hacer con él, y cómo se canjea un código.

Una decisión que ordena todo el módulo: **los límites del plan Gratis existen
en el código pero no se aplican todavía** (ver `LIMITES_ACTIVOS`). Cortarle los
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

#: Interruptor general. En False los límites se calculan y se muestran, pero no
#: bloquean nada. Se enciende el día que se pueda contratar el plan Pro.
LIMITES_ACTIVOS = False


@dataclass(frozen=True)
class Limites:
    """Lo que cada plan permite. `None` es sin límite."""

    ensayos_por_mes: int | None
    carreras_en_meta: int
    #: Si ve el detalle de sus errores por tipo y la curva de fatiga.
    analisis_avanzado: bool


LIMITES: dict[Plan, Limites] = {
    # El plan Gratis tiene que dejar APRENDER completo: las lecciones y el árbol
    # entero están incluidos a propósito. Lo que se limita es el volumen de
    # simulacros, que es lo caro de producir, no el acceso al contenido.
    Plan.GRATIS: Limites(ensayos_por_mes=4, carreras_en_meta=1, analisis_avanzado=False),
    Plan.PRO: Limites(ensayos_por_mes=None, carreras_en_meta=10, analisis_avanzado=True),
    Plan.COLEGIOS: Limites(
        ensayos_por_mes=None, carreras_en_meta=10, analisis_avanzado=True
    ),
}


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


#: Los montos coinciden con los precios de lanzamiento publicados en la página.
#: Si cambian allá, cambian acá: un test verifica que ningún producto quede en
#: cero, que es el error que convertiría el cobro en un regalo silencioso.
PRODUCTOS: dict[str, Producto] = {
    "pro_mensual": Producto(
        id="pro_mensual",
        plan=Plan.PRO,
        dias=30,
        monto=5990,
        asunto="1000paes Pro - 1 mes",
    ),
    "pro_temporada": Producto(
        id="pro_temporada",
        plan=Plan.PRO,
        # Hasta el día de la PAES: se venden como 240 días, que cubre desde
        # cualquier momento del año escolar hasta rendir.
        dias=240,
        monto=34900,
        asunto="1000paes Pro - temporada completa",
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

    return (vigente.plan if vigente else Plan.GRATIS), vigente


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
    limite = LIMITES[plan].ensayos_por_mes
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
    return (not LIMITES_ACTIVOS), motivo


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
