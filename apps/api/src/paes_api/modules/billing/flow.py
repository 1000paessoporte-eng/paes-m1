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
