"""Planes, suscripciones y códigos promocionales.

El producto tenía una página de precios y ningún sistema detrás: todos los
usuarios eran iguales y "plan Pro" era una promesa en HTML. Esto es la
estructura que faltaba.

Está construida para que el día que exista pasarela de pago solo haya que
crear una `Subscription` al confirmar el cobro: nada más del sistema cambia.
Mientras tanto, las suscripciones se pueden otorgar con un código promocional,
que es exactamente lo que se necesita para un colegio piloto.
"""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from paes_api.shared.base import Base

if TYPE_CHECKING:
    from paes_api.modules.users.models import User


class Plan(StrEnum):
    GRATIS = "gratis"
    PRO = "pro"
    COLEGIOS = "colegios"


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"


class Origen(StrEnum):
    """De dónde salió la suscripción. Importa para entender el negocio: no es
    lo mismo un plan que alguien pagó que uno regalado por un código."""

    PAGO = "pago"
    CODIGO = "codigo"
    MANUAL = "manual"


class Subscription(Base):
    """Un plan activo para un usuario, con su fecha de término.

    Un usuario puede tener varias filas a lo largo del tiempo (historial), pero
    solo una activa. Nunca se borra una suscripción vencida: saber qué plan
    tuvo alguien y por cuánto tiempo es justamente lo que exige el premio al
    puntaje nacional, que pide seis meses de Pro en los últimos doce.
    """

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    plan: Mapped[Plan] = mapped_column(Enum(Plan), default=Plan.PRO)
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, index=True
    )
    origen: Mapped[Origen] = mapped_column(Enum(Origen), default=Origen.CODIGO)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    #: Null para una suscripción sin término (por ejemplo, un plan otorgado a
    #: mano de forma indefinida).
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    #: Con qué código se obtuvo, si vino de uno.
    codigo: Mapped[str | None] = mapped_column(String(40), nullable=True)

    user: Mapped["User"] = relationship(back_populates="subscriptions")


class PromoCode(Base):
    """Un código promocional.

    Los límites son de verdad y se comprueban al canjear: un código sin tope de
    usos ni fecha de término no es una campaña, es una puerta abierta. Y la
    escasez que hace que un código valga algo deja de existir si el estudiante
    descubre que nunca se acaba.
    """

    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True, index=True)

    plan: Mapped[Plan] = mapped_column(Enum(Plan), default=Plan.PRO)
    #: Cuántos días de plan entrega.
    dias: Mapped[int] = mapped_column(Integer, default=30)

    #: Cuántas veces se puede canjear en total, y cuántas van.
    usos_maximos: Mapped[int] = mapped_column(Integer, default=1)
    usos: Mapped[int] = mapped_column(Integer, default=0)

    #: Hasta cuándo sirve. Null = sin vencimiento.
    vence_el: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    #: Para qué campaña es, en texto legible.
    descripcion: Mapped[str | None] = mapped_column(String(200), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
