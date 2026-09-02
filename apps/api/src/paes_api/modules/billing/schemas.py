from datetime import datetime

from pydantic import BaseModel, Field

from paes_api.modules.billing.models import Plan


class MiPlanOut(BaseModel):
    """El plan del usuario y lo que puede hacer con él."""

    plan: Plan
    vence_el: datetime | None = None
    #: Cuántos ensayos lleva este mes y cuántos permite su plan (null = sin tope).
    ensayos_usados: int
    ensayos_limite: int | None
    carreras_limite: int
    #: False mientras los límites se informen pero no bloqueen, porque todavía
    #: no se puede contratar el plan Pro.
    limites_activos: bool

    #: True mientras corran los días de prueba, antes del primer cobro. La
    #: pantalla lo necesita para no decir "tu plan vence el 5" cuando lo que
    #: corresponde decir es "te quedan 2 días de prueba y después se cobra":
    #: son dos hechos distintos y confundirlos es cobrar por sorpresa.
    en_trial: bool = False
    #: True si ya pidió no renovar. Conserva el acceso hasta `vence_el`.
    cancelada_al_terminar: bool = False
    #: Si esta cuenta todavía puede tomar la prueba gratis. False si ya la usó
    #: —es una por cuenta— o si el cobro recurrente no está configurado.
    trial_disponible: bool = False
    #: Cuántos días dura la prueba. Sale del mismo lugar que se le manda a
    #: Flow, para que la pantalla no pueda prometer un plazo distinto del que
    #: se cobra.
    trial_dias: int = 0
    #: Lo que se cobra al terminar la prueba, en pesos. Viaja junto al plan y
    #: no en una llamada aparte para que la pantalla que ofrece el trial no
    #: pueda dibujarse con el plazo pero sin el precio: una oferta a medias es
    #: peor que ninguna.
    trial_monto: int = 0
    #: Con qué tarjeta se va a cobrar, para mostrarlo. Nunca el número: solo
    #: marca y últimos cuatro dígitos, tal como "Visa ····4242".
    tarjeta: str | None = None


class CanjearIn(BaseModel):
    codigo: str = Field(min_length=3, max_length=40)


class ProductoOut(BaseModel):
    """Un producto comprable, tal como se muestra en la página."""

    id: str
    plan: str
    dias: int
    monto: int
    asunto: str


class ProductosOut(BaseModel):
    #: False cuando faltan las credenciales de Flow. La web usa esto para no
    #: mostrar un botón de pago que llevaría a un error.
    pago_disponible: bool
    productos: list[ProductoOut]
    #: False cuando falta el plan recurrente en Flow. Sin esto la portada
    #: podría anunciar una prueba gratis que al hacer clic responde error, que
    #: es peor que no anunciarla.
    trial_disponible: bool = False
    trial_dias: int = 0
    #: Lo que se cobra al terminar la prueba, en pesos. Va al lado de la
    #: oferta y no en letra chica: un trial que no dice cuánto se cobra
    #: después es una suscripción vendida a ciegas.
    trial_monto: int = 0


class TrialOut(BaseModel):
    """A dónde hay que mandar a la persona para que inscriba su tarjeta."""

    url: str


class PagarIn(BaseModel):
    #: Solo el identificador del producto. El monto NUNCA viaja desde el
    #: cliente: lo fija el servidor.
    producto: str


class PagarOut(BaseModel):
    #: URL de Flow a la que hay que enviar al usuario.
    url: str
    orden: str
