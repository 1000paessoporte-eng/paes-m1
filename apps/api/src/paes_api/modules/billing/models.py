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
    #: Los tres días de prueba que anteceden al primer cobro. Es su propio
    #: origen y no un `PAGO` con precio cero: son el período por el que NO se
    #: cobró, y contarlo como pago rompería el requisito del premio al puntaje
    #: nacional, que pide seis meses de Pro *pagados* en los últimos doce.
    TRIAL = "trial"


class PagoStatus(StrEnum):
    """Estado de una orden de pago.

    PENDIENTE es el estado inicial y también el de una orden abandonada: quien
    llega al formulario de Flow y cierra la pestaña deja su orden así para
    siempre. No se limpian: sirven para medir cuánta gente se cae en el paso
    del pago, que es justo lo que no se puede ver de otra forma.
    """

    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    RECHAZADO = "rechazado"
    ANULADO = "anulado"


class Pago(Base):
    """Una orden de pago enviada a Flow.

    Existe por dos razones que no se pueden delegar a la pasarela. La primera
    es el monto: el precio se fija acá y se compara contra lo que Flow informa
    al confirmar, de modo que nadie pueda pagar mil pesos por un plan de seis
    mil manipulando la petición. La segunda es la idempotencia: Flow puede
    llamar al webhook más de una vez por la misma orden, y sin un registro
    propio cada llamada extendería la suscripción de nuevo.
    """

    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    #: Identificador propio que viaja a Flow como commerceOrder. Único: es la
    #: llave con que se reconoce la orden al volver.
    orden: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    plan: Mapped[Plan] = mapped_column(Enum(Plan), default=Plan.PRO)
    #: Días de suscripción que otorga esta compra.
    dias: Mapped[int] = mapped_column(Integer, default=30)
    #: Monto en pesos, sin decimales. Es el que se compara al confirmar.
    monto: Mapped[int] = mapped_column(Integer)
    status: Mapped[PagoStatus] = mapped_column(
        Enum(PagoStatus), default=PagoStatus.PENDIENTE
    )
    #: Token que devuelve Flow al crear la orden; con él se consulta el estado.
    token: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    #: Número de orden de Flow, útil para conciliar contra su panel.
    flow_order: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    #: Cuándo se confirmó el pago. NULL mientras no se confirme.
    confirmado_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


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

    #: La suscripción equivalente en Flow, cuando el plan se renueva solo.
    #: Null en todo lo que no es cobro recurrente: un canje de código o un
    #: plan otorgado a mano no tienen contraparte en la pasarela.
    #:
    #: Es la llave con que se reconcilia: la fecha de término de una
    #: suscripción recurrente la manda Flow, no la aritmética de acá.
    flow_subscription_id: Mapped[str | None] = mapped_column(
        String(60), nullable=True, index=True
    )

    #: True cuando la persona pidió no renovar. El acceso SIGUE hasta
    #: `expires_at`.
    #:
    #: Existe porque hasta ahora cancelar ponía `status = CANCELED`, y como
    #: `plan_actual` solo mira las ACTIVE, el acceso se cortaba en el acto: lo
    #: contrario exacto de lo que la pantalla prometía. Apagar la renovación y
    #: terminar la suscripción son dos hechos distintos y necesitan dos
    #: campos distintos.
    cancelada_al_terminar: Mapped[bool] = mapped_column(Boolean, default=False)

    #: Si el período en curso es el de prueba gratuita. Se apaga solo en la
    #: primera reconciliación posterior al primer cobro. Importa para la
    #: pantalla —"te quedan 2 días de prueba" no es lo mismo que "tu plan
    #: vence en 2 días"— y para no contar el trial como mes pagado.
    en_trial: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="subscriptions")


class FlowCustomer(Base):
    """El cliente de Flow donde queda inscrita la tarjeta de una persona.

    Acá NO hay datos de tarjeta y no puede haberlos: el número vive en Flow y
    este servidor guarda solo lo que sirve para mostrarle a alguien con qué
    está pagando ("Visa terminada en 4242") y el identificador con que se le
    pide a Flow que cobre.

    Es uno por usuario. Reinscribir una tarjeta reutiliza el mismo cliente en
    vez de crear otro: un usuario con dos clientes en Flow es un usuario al que
    se le puede terminar cobrando dos veces.
    """

    __tablename__ = "flow_customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, index=True
    )

    #: El `customerId` que devolvió Flow.
    customer_id: Mapped[str] = mapped_column(String(60), unique=True, index=True)

    #: False mientras la tarjeta no esté confirmada. Un cliente creado no es
    #: un cliente con tarjeta: entre `customer/create` y el formulario de Flow
    #: hay una persona que puede cerrar la pestaña.
    registrado: Mapped[bool] = mapped_column(Boolean, default=False)

    #: Para mostrar en pantalla. Nada de esto identifica una tarjeta ni sirve
    #: para cobrar con ella.
    marca: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ultimos4: Mapped[str | None] = mapped_column(String(4), nullable=True)

    #: Token de la última inscripción iniciada, para poder verificarla cuando
    #: la persona vuelve del formulario de Flow.
    token_registro: Mapped[str | None] = mapped_column(
        String(120), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


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
