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
# Suscripciones recurrentes
#
# El cobro puntual de arriba (`payment/create`) sirve para comprar un plazo una
# vez. Lo de acá es distinto: se registra la tarjeta del cliente en Flow y se lo
# suscribe a un plan que Flow cobra solo, mes a mes, hasta que alguien lo cancele.
# El flujo son cuatro pasos: crear el cliente, mandarlo a registrar su tarjeta,
# confirmar que quedó registrada, y recién ahí crear la suscripción.
# ---------------------------------------------------------------------------

#: `status` que devuelve `customer/getRegisterStatus`: 1 = la tarjeta quedó
#: registrada. Cualquier otro valor es que el cliente no terminó o falló.
REGISTRO_OK = 1


def crear_cliente(*, nombre: str, email: str, external_id: str) -> dict[str, Any]:
    """Crea el cliente en Flow. Devuelve `{customerId, ...}`.

    `external_id` es nuestro id de usuario: deja conciliar el cliente de Flow con
    la cuenta sin depender del correo, que la persona puede cambiar.
    """
    datos = _llamar(
        "customer/create",
        {"name": nombre, "email": email, "externalId": external_id},
    )
    if "customerId" not in datos:
        raise FlowError(f"respuesta inesperada de Flow al crear el cliente: {datos}")
    return datos


def registrar_tarjeta(*, customer_id: str, url_retorno: str) -> dict[str, Any]:
    """Pide a Flow la URL donde el cliente registra su tarjeta.

    Devuelve `{url, token}`. Al cliente se lo manda a `url`; cuando termina, Flow
    lo devuelve a `url_retorno` y hay que confirmar con `estado_tarjeta`.
    """
    datos = _llamar(
        "customer/register",
        {"customerId": customer_id, "url_return": url_retorno},
    )
    if "url" not in datos or "token" not in datos:
        raise FlowError(f"respuesta inesperada de Flow al registrar tarjeta: {datos}")
    return datos


def estado_tarjeta(token: str) -> dict[str, Any]:
    """Consulta si el registro de tarjeta terminó bien. Fuente de verdad.

    `status == REGISTRO_OK` significa que la tarjeta quedó guardada y el cliente
    ya se puede suscribir.
    """
    datos = _llamar("customer/getRegisterStatus", {"token": token}, metodo="GET")
    if "status" not in datos:
        raise FlowError(f"respuesta inesperada de Flow al consultar la tarjeta: {datos}")
    return datos


def crear_suscripcion(
    *, plan_id: str, customer_id: str, trial_period_days: int | None = None
) -> dict[str, Any]:
    """Suscribe al cliente al plan recurrente. Devuelve `{subscriptionId, ...}`.

    Con `trial_period_days` Flow no cobra hasta que pasen esos días; el primer
    cobro cae el día que se acaba el trial. Después cobra solo, según el plan.
    """
    params: dict[str, Any] = {"planId": plan_id, "customerId": customer_id}
    if trial_period_days is not None:
        params["trial_period_days"] = trial_period_days
    datos = _llamar("subscription/create", params)
    if "subscriptionId" not in datos:
        raise FlowError(f"respuesta inesperada de Flow al crear la suscripción: {datos}")
    return datos


def estado_suscripcion(subscription_id: str) -> dict[str, Any]:
    """El estado real de una suscripción en Flow, con sus cobros (invoices)."""
    return _llamar("subscription/get", {"subscriptionId": subscription_id}, metodo="GET")


def cancelar_suscripcion(*, subscription_id: str, al_terminar_periodo: bool = True) -> dict[str, Any]:
    """Corta la renovación en Flow.

    `al_terminar_periodo=True` deja que el período ya cobrado se use hasta el
    final y no cobra más; en False corta de inmediato. Se usa el primero: quien
    cancela pagó un mes y ese mes es suyo.
    """
    return _llamar(
        "subscription/cancel",
        {"subscriptionId": subscription_id, "at_period_end": 1 if al_terminar_periodo else 0},
    )


def crear_plan(
    *,
    plan_id: str,
    nombre: str,
    monto: int,
    interval: int,
    trial_period_days: int,
    url_callback: str,
) -> dict[str, Any]:
    """Crea el plan recurrente en Flow. Lo usa `scripts/crear_plan_flow.py`.

    `interval` es la periodicidad del cobro según Flow (mensual, anual, etc.).
    `url_callback` es donde Flow avisará cada cobro de este plan.
    """
    return _llamar(
        "plans/create",
        {
            "planId": plan_id,
            "name": nombre,
            "currency": "CLP",
            "amount": int(monto),
            "interval": interval,
            "interval_count": 1,
            "trial_period_days": trial_period_days,
            "urlCallback": url_callback,
        },
    )
