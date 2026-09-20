"""Inicio de sesión con Microsoft (Entra ID).

Por qué existe además del de Google: muchos colegios chilenos entregan a sus
alumnos una cuenta de Office 365, y ese correo institucional es el que el
estudiante tiene a mano en la sala. "Entra con el correo de tu colegio" es
también lo que hace vendible el producto a un colegio completo.

**El flujo es Authorization Code + PKCE**, no el de Google. Google entrega un
ID token directamente en el navegador; Microsoft ya no recomienda eso para
aplicaciones de página única. Acá:

1. El navegador manda a la persona a Microsoft con un `code_challenge`, que es
   el hash de un secreto que él mismo inventó y que nunca sale de su memoria.
2. Microsoft lo devuelve con un `code` de un solo uso.
3. El navegador le pasa ese `code` --y el secreto original-- a ESTA API.
4. La API canjea el `code` con Microsoft por el ID token.

El canje lo hace el servidor, no el navegador, así que el ID token nunca pasa
por el cliente y llega por TLS directo desde Microsoft. La aplicación es un
cliente *público*: no tiene secreto, y no lo necesita, porque quien no tenga
el `code_verifier` no puede canjear un `code` robado.

No se usa `nonce`: en este flujo lo que ata el token a este navegador es el
`code_verifier`, y un `nonce` que el propio cliente propone y compara no
agregaría garantía, solo la apariencia de una.
"""

import logging
from typing import Any

import jwt
import requests
from jwt import PyJWKClient

logger = logging.getLogger(__name__)

#: `common` acepta cuentas de organización (el colegio, la universidad) y
#: cuentas personales de Microsoft. Restringirlo a un tenant dejaría fuera a
#: todo alumno que no sea de ese colegio.
AUTORIDAD = "https://login.microsoftonline.com/common"
TOKEN_URL = f"{AUTORIDAD}/oauth2/v2.0/token"
JWKS_URL = f"{AUTORIDAD}/discovery/v2.0/keys"

#: Microsoft rota sus claves de firma. El cliente las cachea, así que esto no
#: es un viaje extra en cada inicio de sesión.
_jwks = PyJWKClient(JWKS_URL, cache_keys=True)

TIEMPO_LIMITE = 10


class MicrosoftAuthError(Exception):
    """El código no se pudo canjear, o el token que volvió no es válido."""


def _canjear(code: str, code_verifier: str, redirect_uri: str, client_id: str) -> str:
    """Cambia el código de un solo uso por el ID token, contra Microsoft."""
    try:
        respuesta = requests.post(
            TOKEN_URL,
            data={
                "client_id": client_id,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
                "scope": "openid profile email",
            },
            timeout=TIEMPO_LIMITE,
        )
    except requests.RequestException as err:
        raise MicrosoftAuthError("No se pudo hablar con Microsoft") from err

    cuerpo = respuesta.json() if respuesta.content else {}
    if respuesta.status_code != 200:
        # `error_description` trae el detalle de Microsoft, que sirve en el log
        # pero no se le devuelve a quien llama: ahí solo confundiría.
        logger.warning(
            "Microsoft rechazó el canje: %s", cuerpo.get("error_description", respuesta.text)
        )
        raise MicrosoftAuthError("Microsoft rechazó el inicio de sesión")

    token = cuerpo.get("id_token")
    if not token:
        raise MicrosoftAuthError("Microsoft no devolvió un ID token")
    return token


def _verificar(token: str, client_id: str) -> dict[str, Any]:
    """Comprueba firma, expiración y que el token sea para ESTA aplicación.

    El emisor depende del tenant de la persona --cada colegio es uno-- así que
    sale del propio token y se exige que coincida: así un token legítimo de
    otro tenant no puede presentarse como si fuera de este.
    """
    try:
        sin_verificar = jwt.decode(token, options={"verify_signature": False})
        tid = sin_verificar.get("tid")
        if not tid:
            raise MicrosoftAuthError("El token no dice de qué organización viene")
        clave = _jwks.get_signing_key_from_jwt(token).key
        return jwt.decode(
            token,
            clave,
            algorithms=["RS256"],
            audience=client_id,
            issuer=f"https://login.microsoftonline.com/{tid}/v2.0",
        )
    except MicrosoftAuthError:
        raise
    except (jwt.PyJWTError, jwt.PyJWKClientError) as err:
        raise MicrosoftAuthError(f"El token de Microsoft no es válido: {err}") from err


def identidad(code: str, code_verifier: str, redirect_uri: str, client_id: str) -> dict[str, str]:
    """Quién es la persona, según Microsoft. Lanza MicrosoftAuthError si no.

    Devuelve `sub` (el `oid`, estable aunque le cambien el correo), `email` y
    `name`.
    """
    if not client_id:
        raise MicrosoftAuthError("El inicio de sesión con Microsoft no está configurado")

    claims = _verificar(_canjear(code, code_verifier, redirect_uri, client_id), client_id)

    # `email` no siempre viene en cuentas de organización; ahí el correo va en
    # `preferred_username`, que para Entra es el UPN y es una dirección real.
    correo = claims.get("email") or claims.get("preferred_username") or ""
    if "@" not in correo:
        raise MicrosoftAuthError("La cuenta de Microsoft no expone un correo")

    oid = claims.get("oid")
    if not oid:
        raise MicrosoftAuthError("El token no trae el identificador de la cuenta")

    return {
        "sub": oid,
        "email": correo.lower(),
        "name": claims.get("name") or correo.split("@")[0],
    }
