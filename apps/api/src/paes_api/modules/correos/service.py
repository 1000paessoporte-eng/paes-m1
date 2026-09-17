"""Correos que la plataforma le escribe a sus usuarios.

Acá viven los dos que NO son respuesta a una acción de seguridad (esos --
recuperar contraseña-- están en `modules/users/service.py`):

1. **Bienvenida**: se manda una vez, al crear la cuenta.
2. **Difusión**: un correo escrito a mano que se le manda a muchas cuentas.

Dos reglas ordenan todo lo de abajo, y las dos existen por la misma razón: el
dominio del remitente es uno solo, y si se quema mandando correo no pedido
también dejan de llegar los de recuperar contraseña, que son los únicos que
alguien realmente necesita.

**Regla 1 -- la bienvenida nunca puede romper el registro.** Se manda después
de que la cuenta ya está creada y confirmada en la base, y cualquier fallo del
proveedor queda en el log. Que el correo no salga es un problema; que alguien
no pueda registrarse porque el correo no salió es uno mucho peor.

**Regla 2 -- la difusión respeta el opt-out y lo ofrece siempre.** `difundir`
se salta a quien apagó los avisos en su perfil (`recordatorios_email`) y agrega
el pie de baja al final del cuerpo, sin que quien escribe tenga que acordarse.
No es solo cortesía: la Ley 19.496 exige que toda comunicación promocional
identifique al remitente e incluya una forma de pedir que no se le escriba más.
"""

import logging
import time
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.email import CorreoNoEnviado, send_email
from paes_api.modules.users.models import User

logger = logging.getLogger(__name__)

#: A quién se le escribe en una difusión.
#:
#: `correo` son las cuentas con contraseña propia --las que se registraron
#: escribiendo su correo-- y `google` las que entraron con el botón de Google.
#: La distinción importa porque no son el mismo público: quien entró con Google
#: nunca tuvo que confirmar nada, y quien se registró con correo ya demostró
#: que esa dirección la lee.
PUBLICOS = ("todos", "correo", "google")


def _pie_de_baja(url: str) -> str:
    return (
        "\n\n—\n1000paes — preparación PAES\n"
        f"Si no quieres recibir estos correos, apágalos en tu perfil: {url}/perfil"
    )


def destinatarios(db: Session, publico: str = "todos") -> Sequence[User]:
    """Las cuentas que recibirían una difusión, ya filtradas por el opt-out.

    Se resuelve en una consulta y no recorriendo la tabla en Python porque el
    resultado se muestra ANTES de mandar nada: la parte más cara de equivocarse
    en un correo masivo es no saber a cuántas personas se le va a mandar.
    """
    if publico not in PUBLICOS:
        raise ValueError(f"Público desconocido: {publico!r}. Opciones: {', '.join(PUBLICOS)}")

    consulta = select(User).where(User.recordatorios_email.is_(True))
    if publico == "correo":
        consulta = consulta.where(User.hashed_password.is_not(None))
    elif publico == "google":
        consulta = consulta.where(User.google_sub.is_not(None))

    return db.execute(consulta.order_by(User.id)).scalars().all()


def difundir(
    db: Session,
    asunto: str,
    cuerpo: str,
    publico: str = "todos",
    *,
    prueba: bool = False,
    solo: str | None = None,
    pausa: float = 1.0,
) -> dict[str, object]:
    """Manda un correo escrito a mano. Devuelve el recuento de lo que hizo.

    `prueba=True` no manda nada y devuelve la lista de a quién le habría
    mandado: es el ensayo obligatorio antes de escribirle a gente real, porque
    un correo masivo no se puede deshacer. `solo` manda el mensaje real a una
    sola dirección --la propia-- para ver cómo se ve al llegar.

    `pausa` son los segundos de espera entre correo y correo. No es paranoia:
    los proveedores cortan al remitente que abre cien conexiones seguidas, y
    ser cortado a mitad de tanda deja al azar quién recibió y quién no.

    Un envío que falla NO detiene la tanda, por lo mismo que en los
    recordatorios: una dirección rebotada no puede dejar sin correo a las
    demás. Se cuenta aparte y se sigue.
    """
    url = get_settings().frontend_url
    cuerpo_final = cuerpo.rstrip() + _pie_de_baja(url)

    if solo is not None:
        send_email(solo, asunto, cuerpo_final)
        return {"enviados": 1, "fallidos": 0, "destinatarios": [solo], "prueba": False}

    cuentas = destinatarios(db, publico)
    correos = [u.email for u in cuentas]

    if prueba:
        return {
            "enviados": 0,
            "fallidos": 0,
            "destinatarios": correos,
            "prueba": True,
        }

    enviados = 0
    fallidos = 0
    for indice, user in enumerate(cuentas):
        try:
            send_email(user.email, asunto, cuerpo_final)
        except CorreoNoEnviado:
            logger.exception("No se pudo enviar la difusión a %s", user.email)
            fallidos += 1
            continue
        enviados += 1
        if pausa and indice < len(cuentas) - 1:
            time.sleep(pausa)

    return {
        "enviados": enviados,
        "fallidos": fallidos,
        "destinatarios": correos,
        "prueba": False,
    }


def enviar_bienvenida(user: User) -> bool:
    """Le da la bienvenida a una cuenta recién creada. Nunca lanza.

    Devuelve si el correo salió, para quien quiera contarlo; quien la llama en
    el flujo de registro puede ignorar el valor con tranquilidad, que es
    justamente el punto: este correo es un extra, y su fallo no puede
    convertirse en el fallo del registro.

    El texto no promete nada que la plataforma no haga hoy y no mete urgencia
    inventada --nada de "quedan X cupos"--: el primer correo es el que decide
    si los siguientes se abren o se marcan como spam.
    """
    ajustes = get_settings()
    nombre = user.name.split(" ")[0] if user.name else "hola"
    asunto = f"{nombre}, tu cuenta en 1000paes ya está lista"
    cuerpo = (
        f"Hola {nombre}:\n\n"
        "Tu cuenta en 1000paes ya está creada. Con ella puedes rendir ensayos "
        "PAES con preguntas nuevas, ver tu puntaje estimado en la escala 100-1000 "
        "y saber en qué contenidos estás flojo.\n\n"
        "Para partir, lo más útil es rendir un ensayo corto (20 preguntas, unos "
        "40 minutos). De ahí sale tu primer puntaje de referencia:\n"
        f"{ajustes.frontend_url}/examen\n\n"
        "Si tienes dudas, responde este correo."
    )
    cuerpo += _pie_de_baja(ajustes.frontend_url)

    try:
        send_email(user.email, asunto, cuerpo)
    except CorreoNoEnviado:
        logger.exception("No se pudo enviar la bienvenida a %s", user.email)
        return False
    return True
