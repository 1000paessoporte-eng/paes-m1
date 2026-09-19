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
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.email import CorreoNoEnviado, send_email
from paes_api.modules.goals.service import FECHA_PAES
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


#: A dónde escribir. `no-responder@1000paes.cl` no tiene buzón --el dominio no
#: tiene MX--, así que "responde este correo" mandaba las dudas a ninguna parte.
CONTACTO = "1000paessoporte@gmail.com"


def presentacion(url: str) -> str:
    """Qué ofrece la plataforma y cómo aprovecharla. Lo comparten la bienvenida
    a cuentas nuevas y la difusión a las que ya existían, para que las dos
    cuenten lo mismo.

    Cada cifra sale del README ("Contenido actual", verificado con
    `verificar_banco.py`): si el banco cambia mucho, se actualiza acá también.
    Nada de urgencia inventada ni promesas de puntaje.
    """
    dias = max(0, (FECHA_PAES - datetime.now(UTC)).days)
    fecha = f" Quedan {dias} días para la PAES regular." if dias else ""
    return (
        "LO QUE TIENES DISPONIBLE\n\n"
        "• Las cinco pruebas: Competencia Lectora, Matemática M1 y M2, Historia y "
        "Ciencias Sociales, y Ciencias.\n"
        "• Más de 6.400 preguntas originales. En cada una puedes ver el desarrollo "
        "completo y por qué cada alternativa incorrecta lo es.\n"
        "• Tu puntaje en escala 100-1000, calculado con las tablas oficiales del "
        "DEMRE, con desglose por eje y por tema.\n"
        "• Árbol de Habilidades: el temario completo en 95 lecciones, con teoría, "
        "ejercicios resueltos paso a paso y el error más común de cada tema.\n"
        "• Mi meta: agrega las carreras que te interesan y calcula tu puntaje "
        "ponderado con las ponderaciones oficiales.\n\n"
        "CÓMO EMPEZAR\n\n"
        "1. Rinde un ensayo corto (20 preguntas, unos 40 minutos). Es tu punto de "
        f"partida:\n   {url}/examen\n"
        "2. Revisa cada error con su desarrollo. Ahí se aprende más que "
        "respondiendo preguntas nuevas.\n"
        "3. Sigue la recomendación del Árbol de Habilidades, que te indica qué tema "
        f"reforzar primero:\n   {url}/arbol\n"
        f"4. Define tu meta para saber cuántos puntos te faltan:\n   {url}/meta\n\n"
        "DOS DATOS QUE CONVIENE SABER\n\n"
        "• En la PAES las respuestas incorrectas no descuentan puntaje: nunca dejes "
        "una pregunta en blanco.\n"
        "• Rinde más practicar un poco casi todos los días que una sesión larga el "
        f"fin de semana.{fecha}\n\n"
        "Los domingos te enviaremos un resumen de tu semana: lo que practicaste, "
        "cómo va tu puntaje y qué te conviene estudiar después.\n\n"
        f"¿Dudas o sugerencias? Escríbenos a {CONTACTO}."
    )


def enviar_bienvenida(user: User) -> bool:
    """Le da la bienvenida a una cuenta recién creada. Nunca lanza.

    Devuelve si el correo salió, para quien quiera contarlo; quien la llama en
    el flujo de registro puede ignorar el valor con tranquilidad, que es
    justamente el punto: este correo es un extra, y su fallo no puede
    convertirse en el fallo del registro.

    El primer correo es el que decide si los siguientes se abren o se marcan
    como spam: por eso informa, no vende.
    """
    ajustes = get_settings()
    nombre = user.name.split(" ")[0] if user.name else ""
    saludo = f"Hola {nombre}:" if nombre else "Hola:"
    asunto = f"{nombre}, te damos la bienvenida a 1000paes" if nombre else "Te damos la bienvenida a 1000paes"
    cuerpo = (
        f"{saludo}\n\n"
        "Tu cuenta en 1000paes ya está lista. Te damos la bienvenida a la "
        "plataforma para preparar la PAES con ensayos, lecciones y un seguimiento "
        "real de tu avance.\n\n"
        + presentacion(ajustes.frontend_url)
    )
    cuerpo += _pie_de_baja(ajustes.frontend_url)

    try:
        send_email(user.email, asunto, cuerpo)
    except CorreoNoEnviado:
        logger.exception("No se pudo enviar la bienvenida a %s", user.email)
        return False
    return True
