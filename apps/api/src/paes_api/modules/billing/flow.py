"""Cliente de Flow, la pasarela de pago.

Dos decisiones de seguridad ordenan este archivo y conviene decirlas antes que
el código.

**El navegador no es fuente de verdad.** Flow devuelve al usuario a una URL de
retorno cuando termina, pero esa vuelta la controla el navegador: cualquiera
puede escribirla a mano. La suscripción se activa únicamente cuando el webhook
recibe un token y este módulo le pregunta a Flow, de servidor a servidor, si esa
orden está realmente pagada.

**El monto se compara siempre.** Flow informa cuánto se pagó, y el llamador debe
contrastarlo contra el precio que fijó al crear la orden. Sin esa comparación,
manipular la petición inicial permitiría comprar un plan de seis mil pesos por
cien.
"""

import hashlib
import hmac
from typing import Any

import requests

from paes_api.core.config import get_settings

#: Cuánto se espera a Flow antes de rendirse.
#:
#: Se subió de 15 a 25 porque el ambiente de PRODUCCIÓN de Flow resultó ser
#: bastante más lento que el sandbox: con 15 segundos daba read timeout de
#: forma consistente mientras el sandbox respondía al instante. El techo lo
#: pone Vercel, que corta la función a los 30, así que 25 deja margen para
#: devolver un error ordenado en vez de que la petición muera sin respuesta.
TIMEOUT = 25

#: Códigos de estado que devuelve Flow en `status`.
PAGADA = 2
RECHAZADA = 3
ANULADA = 4


class FlowError(Exception):
    """Flow respondió con error o no respondió."""


class FlowNoConfigurado(Exception):
    """Faltan las credenciales: el cobro está desactivado."""


def esta_configurado() -> bool:
    s = get_settings()
    return bool(s.flow_api_key and s.flow_secret_key)


def firmar(params: dict[str, Any]) -> str:
    """Firma HMAC-SHA256 de los parámetros, como exige Flow.

    El orden importa y no es negociable: Flow concatena los pares ordenados
    ALFABÉTICAMENTE por nombre. Firmar en el orden en que uno los escribió
    produce una firma válida en apariencia que Flow rechaza, y el mensaje de
    error no dice que el problema sea el orden.
    """
    secreto = get_settings().flow_secret_key.encode()
    cadena = "".join(f"{k}{params[k]}" for k in sorted(params))
    return hmac.new(secreto, cadena.encode(), hashlib.sha256).hexdigest()


def _llamar(recurso: str, params: dict[str, Any], metodo: str = "POST") -> dict[str, Any]:
    if not esta_configurado():
        raise FlowNoConfigurado
    s = get_settings()
    cuerpo = {"apiKey": s.flow_api_key, **params}
    cuerpo["s"] = firmar(cuerpo)
    url = f"{s.flow_base_url.rstrip('/')}/{recurso}"

    try:
        if metodo == "POST":
            r = requests.post(url, data=cuerpo, timeout=TIMEOUT)
        else:
            r = requests.get(url, params=cuerpo, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise FlowError(f"no se pudo contactar a Flow: {e}") from e

    if r.status_code >= 400:
        # El cuerpo de Flow trae el motivo; se propaga recortado porque termina
        # en un log y no en la pantalla del usuario.
        raise FlowError(f"Flow respondió {r.status_code}: {r.text[:200]}")
    try:
        return r.json()
    except ValueError as e:
        raise FlowError("Flow devolvió una respuesta que no es JSON") from e


def crear_orden(
    *,
    orden: str,
    monto: int,
    asunto: str,
    email: str,
    url_confirmacion: str,
    url_retorno: str,
) -> dict[str, Any]:
    """Crea la orden y devuelve `{token, url, flowOrder}`.

    Al usuario hay que enviarlo a `url` + "?token=" + `token`.
    """
    datos = _llamar(
        "payment/create",
        {
            "commerceOrder": orden,
            "subject": asunto,
            "currency": "CLP",
            # Flow rechaza montos con decimales en pesos chilenos.
            "amount": int(monto),
            "email": email,
            "urlConfirmation": url_confirmacion,
            "urlReturn": url_retorno,
        },
    )
    if "token" not in datos or "url" not in datos:
        raise FlowError(f"respuesta inesperada de Flow al crear la orden: {datos}")
    return datos


def estado(token: str) -> dict[str, Any]:
    """Consulta el estado real de una orden. Es la única fuente de verdad."""
    datos = _llamar("payment/getStatus", {"token": token}, metodo="GET")
    if "status" not in datos:
        raise FlowError(f"respuesta inesperada de Flow al consultar: {datos}")
    return datos


# ---------------------------------------------------------------------------
# Suscripciones: clientes, planes y cobro recurrente
# ---------------------------------------------------------------------------
#
# El cobro recurrente de Flow es un mecanismo DISTINTO del de `payment/create`,
# no una variante suya. Un pago normal es una orden que alguien paga una vez;
# una suscripción son tres piezas que hay que armar en orden:
#
#   1. Un CLIENTE en Flow (`customer/create`), que es donde queda inscrita la
#      tarjeta. La tarjeta la guarda Flow, nunca este servidor.
#   2. La INSCRIPCIÓN de esa tarjeta (`customer/register`), que manda a la
#      persona a un formulario de Flow y vuelve con un token que hay que
#      verificar de servidor a servidor.
#   3. La SUSCRIPCIÓN propiamente tal (`subscription/create`), que asocia el
#      cliente a un plan y desde ahí Flow cobra solo, mes a mes.
#
# La trampa que cuesta una tarde: los nombres de los parámetros NO siguen una
# convención única. `payment/create` usa `urlReturn` en camelCase y
# `customer/register` usa `url_return` con guion bajo. Escribir el que uno
# esperaría hace que Flow responda un error que no menciona el parámetro.


def cliente_crear(*, nombre: str, email: str, externo: str) -> dict[str, Any]:
    """Crea el cliente en Flow y devuelve `{customerId, ...}`.

    `externo` es nuestro propio identificador del usuario. Sirve para conciliar
    en el panel de Flow sin tener que cruzar correos, y para reconocer al
    cliente si alguna vez hay que reconstruir la relación desde ese lado.
    """
    datos = _llamar(
        "customer/create",
        {"name": nombre, "email": email, "externalId": externo},
    )
    if "customerId" not in datos:
        raise FlowError(f"respuesta inesperada de Flow al crear el cliente: {datos}")
    return datos


def cliente_registrar(*, customer_id: str, url_retorno: str) -> dict[str, Any]:
    """Inicia la inscripción de la tarjeta. Devuelve `{url, token}`.

    Al usuario hay que enviarlo a `url` + "?token=" + `token`, igual que en un
    pago. Flow lo devuelve a `url_retorno` cuando termina, con el token en el
    cuerpo de un POST.

    Ojo con `url_return`: acá va con guion bajo. En `payment/create` el mismo
    concepto se llama `urlReturn`.
    """
    datos = _llamar(
        "customer/register",
        {"customerId": customer_id, "url_return": url_retorno},
    )
    if "token" not in datos or "url" not in datos:
        raise FlowError(f"respuesta inesperada de Flow al inscribir tarjeta: {datos}")
    return datos


#: Lo que devuelve `customer/getRegisterStatus` en `status` cuando la tarjeta
#: quedó efectivamente inscrita. Cualquier otro valor significa que la persona
#: abandonó el formulario o que el banco rechazó la inscripción.
TARJETA_INSCRITA = "1"


def cliente_estado_registro(token: str) -> dict[str, Any]:
    """Verifica una inscripción de tarjeta. Es la única fuente de verdad.

    El token llega por el navegador, así que por sí solo no prueba nada: lo que
    vale es lo que Flow responde a esta consulta de servidor a servidor.
    """
    datos = _llamar("customer/getRegisterStatus", {"token": token}, metodo="GET")
    if "status" not in datos:
        raise FlowError(f"respuesta inesperada de Flow al verificar la tarjeta: {datos}")
    return datos


def tarjeta_quedo_inscrita(datos: dict[str, Any]) -> bool:
    """Si la respuesta de `cliente_estado_registro` confirma la inscripción.

    Flow ha devuelto ese `status` tanto como número como como texto según el
    ambiente, así que se compara en string en vez de confiar en el tipo.
    """
    return str(datos.get("status", "")).strip() == TARJETA_INSCRITA


def suscripcion_crear(
    *, plan_id: str, customer_id: str, trial_dias: int | None = None
) -> dict[str, Any]:
    """Suscribe al cliente al plan. Devuelve el objeto de suscripción de Flow.

    `trial_dias` se manda SIEMPRE aunque el plan ya lo traiga configurado: es
    lo que se le prometió a esta persona en pantalla, y dejarlo depender de
    cómo quedó creado el plan en Flow significa que cambiar el plan en su panel
    cambiaría en silencio lo que dice la web. Acá manda el código.
    """
    params: dict[str, Any] = {"planId": plan_id, "customerId": customer_id}
    if trial_dias is not None:
        params["trial_period_days"] = int(trial_dias)

    datos = _llamar("subscription/create", params)
    if "subscriptionId" not in datos:
        raise FlowError(f"respuesta inesperada de Flow al suscribir: {datos}")
    return datos


def suscripcion_estado(subscription_id: str) -> dict[str, Any]:
    """El estado real de la suscripción en Flow.

    De acá sale `period_end`, que es la fecha hasta la que el acceso está
    pagado. Se usa ESA y no una cuenta propia de días: quien decide cuándo
    termina un período cobrado es la pasarela que cobra, y cualquier
    aritmética local termina desviándose el día que Flow reintenta un cobro,
    aplica un cupón o mueve la fecha de facturación.
    """
    datos = _llamar(
        "subscription/get", {"subscriptionId": subscription_id}, metodo="GET"
    )
    if "subscriptionId" not in datos:
        raise FlowError(f"respuesta inesperada de Flow al consultar suscripción: {datos}")
    return datos


def suscripcion_cancelar(
    subscription_id: str, *, al_terminar: bool = True
) -> dict[str, Any]:
    """Cancela la suscripción en Flow.

    `al_terminar` en True corta la RENOVACIÓN y deja correr el período ya
    cobrado hasta su fecha. En False corta de inmediato, que es cobrarle a
    alguien días que después no puede usar. Por eso el valor por omisión es
    True y el otro camino no lo usa nadie hoy.
    """
    return _llamar(
        "subscription/cancel",
        {"subscriptionId": subscription_id, "at_period_end": 1 if al_terminar else 0},
    )


def plan_crear(
    *,
    plan_id: str,
    nombre: str,
    monto: int,
    trial_dias: int,
    url_callback: str,
    intervalo: int = 3,
) -> dict[str, Any]:
    """Crea el plan de cobro recurrente en Flow.

    Se corre UNA vez por ambiente, desde `scripts/crear_plan_flow.py`, no en
    caliente: un plan es un objeto que vive en Flow y crearlo desde el camino
    normal de la aplicación significaría que un despliegue puede duplicarlo.

    `intervalo` 3 es mensual en la nomenclatura de Flow (1 diario, 2 semanal,
    3 mensual, 4 anual).
    """
    return _llamar(
        "plans/create",
        {
            "planId": plan_id,
            "name": nombre,
            "currency": "CLP",
            "amount": int(monto),
            "interval": intervalo,
            "interval_count": 1,
            "trial_period_days": int(trial_dias),
            "urlCallback": url_callback,
        },
    )


def plan_estado(plan_id: str) -> dict[str, Any]:
    """Lee un plan de Flow. Sirve para comprobar que existe antes de suscribir."""
    return _llamar("plans/get", {"planId": plan_id}, metodo="GET")
