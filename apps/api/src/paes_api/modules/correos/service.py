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
from collections.abc import Collection, Sequence
from datetime import UTC, datetime
from html import escape

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.email import CorreoNoEnviado, send_email
from paes_api.modules.correos import plantilla
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
        "\n\n—\n1000paes — preparación PAES\n1000PAES SpA · RUT 78.516.038-K\n"
        f"Si no quieres recibir estos correos, apágalos en tu perfil: {url}/perfil"
    )


def destinatarios(
    db: Session, publico: str = "todos", excluir: Collection[str] = ()
) -> Sequence[User]:
    """Las cuentas que recibirían una difusión, ya filtradas por el opt-out.

    Se resuelve en una consulta y no recorriendo la tabla en Python porque el
    resultado se muestra ANTES de mandar nada: la parte más cara de equivocarse
    en un correo masivo es no saber a cuántas personas se le va a mandar.

    `excluir` deja fuera direcciones concretas. Hace falta porque en la base
    conviven cuentas que no son de nadie: la demo (`demo@paes-m1.cl`, un
    dominio que ni siquiera existe) y las de revisión interna. Escribirles no
    solo es inútil: una dirección inexistente rebota, y los rebotes le bajan la
    reputación al dominio, que es de lo que depende que el resto llegue.
    """
    if publico not in PUBLICOS:
        raise ValueError(f"Público desconocido: {publico!r}. Opciones: {', '.join(PUBLICOS)}")

    consulta = select(User).where(User.recordatorios_email.is_(True))
    if publico == "correo":
        consulta = consulta.where(User.hashed_password.is_not(None))
    elif publico == "google":
        consulta = consulta.where(User.google_sub.is_not(None))

    fuera = {correo.strip().lower() for correo in excluir if correo.strip()}
    cuentas = db.execute(consulta.order_by(User.id)).scalars().all()
    if not fuera:
        return cuentas
    return [u for u in cuentas if u.email.lower() not in fuera]


def _primer_nombre(user: User) -> str:
    return user.name.split(" ")[0] if user.name else ""


def difundir(
    db: Session,
    asunto: str,
    cuerpo: str,
    publico: str = "todos",
    *,
    prueba: bool = False,
    solo: str | None = None,
    pausa: float = 1.0,
    html: str | None = None,
    nombre_solo: str = "",
    excluir: Collection[str] = (),
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

    `html`, si viene, va como versión HTML del mismo correo. Debe traer su
    propio pie de baja (`plantilla.documento` lo pone). En asunto, cuerpo y
    html, `{nombre}` se reemplaza por el primer nombre de cada destinatario
    --escapado en el HTML--; con `solo`, por `nombre_solo`.
    """
    url = get_settings().frontend_url
    cuerpo_final = cuerpo.rstrip() + _pie_de_baja(url)

    def _para(nombre: str) -> tuple[str, str, str | None]:
        return (
            asunto.replace("{nombre}", nombre),
            cuerpo_final.replace("{nombre}", nombre),
            html.replace("{nombre}", escape(nombre)) if html else None,
        )

    if solo is not None:
        send_email(solo, *_para(nombre_solo))
        return {"enviados": 1, "fallidos": 0, "destinatarios": [solo], "prueba": False}

    cuentas = destinatarios(db, publico, excluir)
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
            send_email(user.email, *_para(_primer_nombre(user)))
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


#: A dónde escribir. El dominio no tiene MX --Resend solo manda--, así que
#: ninguna dirección `@1000paes.cl` recibe: una respuesta llega acá porque
#: `smtp_reply_to` la redirige (ver `core/config.py`), y este es el mismo buzón
#: para quien prefiera escribir a mano.
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
        "Una cosa: responde este correo contándonos qué prueba te cuesta más y te "
        "decimos por dónde conviene partir. Lo leemos nosotros.\n\n"
        f"¿Dudas o sugerencias? Escríbenos a {CONTACTO}."
    )


_MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre")
FECHA_PAES_TEXTO = f"{FECHA_PAES.day} de {_MESES[FECHA_PAES.month - 1]}"


def _dias_paes() -> int:
    return max(0, (FECHA_PAES - datetime.now(UTC)).days)


def bienvenida_html(nombre: str, url: str, *, cuenta_existente: bool = False) -> str:
    """La bienvenida en HTML. Cuenta lo mismo que `presentacion()`, con la
    identidad del sitio. `nombre` llega sin escapar; acá se escapa."""
    p = plantilla
    primer = f"<span style=\"color:#a9a8a4\">{escape(nombre)},</span><br>" if nombre else ""
    if cuenta_existente:
        antetitulo = "Bienvenida a la nueva 1000paes"
        titulo = f"{primer}todo lo que necesitas para tu PAES, en un solo lugar"
        bajada = (
            "Gracias por ser parte de 1000paes. La plataforma creció mucho desde que "
            "creaste tu cuenta: esto es lo que puedes hacer hoy."
        )
    else:
        antetitulo = "Tu cuenta está lista"
        titulo = f"{primer}te damos la bienvenida a 1000paes"
        bajada = (
            "La plataforma para preparar la PAES con ensayos, lecciones y un "
            "seguimiento real de tu avance."
        )

    portada = p.portada(
        url=url,
        antetitulo=antetitulo,
        titulo_html=titulo,
        bajada=bajada,
        boton_texto="Rinde tu primer ensayo",
        enlace=f"{url}/examen",
    )
    cuerpo = (
        p.cifras([
            ("6.400+", "preguntas originales"),
            ("95", "lecciones paso a paso"),
            ("100–1000", "puntaje con tablas DEMRE"),
        ])
        + p.cuenta_regresiva(url, _dias_paes(), FECHA_PAES_TEXTO)
        + p.titulo("Las cinco pruebas")
        + p.pruebas()
        + p.titulo("Lo que tienes disponible")
        + p.funcion(
            "Modo Ensayo",
            "Eliges prueba, ejes, cantidad de preguntas y ritmo. El tiempo es "
            "proporcional al oficial.",
            "#1d4ed8",
        )
        + p.funcion(
            "Revisión de cada pregunta",
            "El desarrollo completo y por qué cada alternativa incorrecta lo es. "
            "Ahí es donde más se aprende.",
            "#0f766e",
        )
        + p.funcion(
            "Árbol de Habilidades",
            "El temario completo en 95 lecciones, con teoría, ejercicios resueltos "
            "y el error más común de cada tema. Te dice qué reforzar primero.",
            "#7e22ce",
        )
        + p.funcion(
            "Mi meta",
            "Agrega las carreras que te interesan y calcula tu puntaje ponderado con "
            "las ponderaciones oficiales.",
            "#b45309",
        )
        + p.titulo("Cómo empezar")
        + p.pasos([
            ("Rinde un ensayo corto", "20 preguntas, unos 40 minutos. Es tu punto de partida.", f"{url}/examen"),
            ("Revisa tus errores", "Cada pregunta trae su desarrollo paso a paso.", None),
            ("Sigue el Árbol de Habilidades", "Te indica qué tema reforzar primero.", f"{url}/arbol"),
            ("Define tu meta", "Para saber cuántos puntos te faltan.", f"{url}/meta"),
        ])
        + p.titulo("Dos datos que conviene saber")
        + p.nota(
            "<strong>Las respuestas incorrectas no descuentan puntaje</strong> en la "
            "PAES: nunca dejes una pregunta en blanco.<br><br>"
            "<strong>Practicar un poco casi todos los días</strong> rinde más que una "
            "sesión larga el fin de semana."
        )
        + p.parrafo(
            f'<span style="color:{p.APAGADO};font-size:14px">Los domingos te enviaremos '
            "un resumen de tu semana: lo que practicaste, cómo va tu puntaje y qué te "
            "conviene estudiar después.</span>"
        )
        + p.parrafo(
            "<strong>Una cosa:</strong> responde este correo contándonos qué prueba te "
            "cuesta más y te decimos por dónde conviene partir. Lo leemos nosotros."
        )
        + p.parrafo("Mucho éxito en tu preparación.<br><strong>El equipo de 1000paes</strong>")
    )
    return p.documento(
        url=url,
        preencabezado="Las cinco pruebas, 95 lecciones y tu puntaje con tablas DEMRE.",
        portada_html=portada,
        cuerpo=cuerpo,
        contacto=CONTACTO,
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
        send_email(user.email, asunto, cuerpo, bienvenida_html(nombre, ajustes.frontend_url))
    except CorreoNoEnviado:
        logger.exception("No se pudo enviar la bienvenida a %s", user.email)
        return False
    return True


def bienvenida_existentes(url: str) -> tuple[str, str, str]:
    """Asunto, texto y HTML de la bienvenida a cuentas que ya existían, con
    `{nombre}` para que `difundir` lo personalice. El texto no lleva pie de
    baja: `difundir` lo agrega; el HTML sí, porque lo pone la plantilla."""
    asunto = "{nombre}, te damos la bienvenida a la nueva 1000paes"
    cuerpo = (
        "Hola {nombre}:\n\n"
        "Gracias por ser parte de 1000paes. La plataforma creció mucho desde que "
        "creaste tu cuenta, y queremos contarte todo lo que puedes hacer hoy para "
        "preparar la PAES.\n\n"
        + presentacion(url)
        + "\n\nMucho éxito en tu preparación.\nEl equipo de 1000paes"
    )
    return asunto, cuerpo, bienvenida_html("{nombre}", url, cuenta_existente=True)
