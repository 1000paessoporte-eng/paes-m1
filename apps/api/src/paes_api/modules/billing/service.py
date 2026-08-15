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

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from paes_api.modules.billing.models import (
    Origen,
    Plan,
    PromoCode,
    Subscription,
    SubscriptionStatus,
)
from paes_api.modules.exam_focus.models import ExamAttempt

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
