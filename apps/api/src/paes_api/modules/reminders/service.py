"""Recordatorios por correo para no perder la racha.

A quién se le escribe, cuándo, y qué dice. Tres reglas ordenan todo:

1. **Nunca a quien lo apagó.** El opt-out es inmediato y definitivo hasta que
   la persona lo vuelva a activar.
2. **Nunca dos días seguidos.** Un recordatorio diario deja de ser un
   recordatorio y pasa a ser acoso; a la tercera vez se marca como spam y se
   pierde el dominio para todos los correos, incluidos los de recuperar
   contraseña.
3. **Solo si sirve.** A quien ya rindió hoy no se le escribe, y a quien lleva
   dos meses sin entrar tampoco: ese no se convence con un correo, y mandárselo
   solo daña la reputación del remitente.

Y una cuarta que sale de las otras: **un correo al día como máximo.** El
domingo no hay recordatorio porque ese día sale el resumen semanal
(`resumen.py`). Tres avisos diarios se pidieron y se descartaron: con el plan
gratis de Resend (100 correos al día) alcanzaría para 33 alumnos, y el
tercer aviso del día es el que se marca como spam.

El cron corre a las 20:00 UTC: las 17:00 en Chile en horario de verano y las
16:00 en invierno. Es la hora en que se sale del colegio y todavía queda tarde
para estudiar; a las 19:00, como era antes, ya compite con la comida y el
cansancio.
"""

import logging
import time
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.email import CorreoNoEnviado, send_email
from paes_api.modules.exam_focus.models import ExamAttempt
from paes_api.modules.goals.service import FECHA_PAES
from paes_api.modules.skill_tree.models import Subject
from paes_api.modules.skill_tree.service import get_recommended_node
from paes_api.modules.users.models import User

logger = logging.getLogger(__name__)

#: Días mínimos entre dos recordatorios a la misma persona.
DESCANSO_DIAS = 2
#: Sobre esto, la cuenta se considera dormida y se deja de insistir.
ABANDONO_DIAS = 45
#: Segundos de envío antes de cortar la tanda. La función muere a los 30 s
#: (`vercel.json`) y cada correo por SMTP tarda cerca de uno; si se corta a la
#: fuerza no queda ni el recuento. Quien no alcanzó entra en la pasada siguiente.
PRESUPUESTO_SEGUNDOS = 22
#: Lunes = 0 ... domingo = 6. El domingo sale el resumen semanal.
DIA_DEL_RESUMEN = 6


def pie_de_baja(url: str) -> str:
    """La forma de dejar de recibir correos, obligatoria (Ley 19.496)."""
    return (
        "\n\n—\n1000paes — preparación PAES\n"
        f"Si no quieres recibir estos correos, apágalos en tu perfil: {url}/perfil"
    )


def materia_principal(user: User) -> Subject:
    """La prueba que el alumno marcó primero en su perfil; M1 si no marcó."""
    primera = (user.pruebas_objetivo or "").split(",")[0].strip()
    try:
        return Subject(primera)
    except ValueError:
        return Subject.M1


def siguiente_paso(db: Session, user: User, url: str) -> tuple[str, str] | None:
    """El nodo que más le conviene estudiar ahora, con su enlace directo.

    Es lo que convierte un "estudia" genérico en algo que se puede hacer en 15
    minutos sin decidir nada. Nunca lanza: si la recomendación falla, el correo
    sale igual con el enlace al ensayo.
    """
    try:
        nodo = get_recommended_node(db, user.id, materia_principal(user))
    except Exception:
        logger.exception("No se pudo calcular el nodo recomendado de %s", user.id)
        return None
    if nodo is None:
        return None
    return nodo.name, f"{url}/practicar/{nodo.code}"


def _con_zona(momento: datetime | None) -> datetime | None:
    """Fecha comparable, venga de donde venga.

    Postgres devuelve estas columnas con zona horaria y SQLite —el motor de los
    tests— sin ella. Restar una de otra revienta, así que se normalizan a UTC
    antes de cualquier comparación.
    """
    if momento is None:
        return None
    return momento if momento.tzinfo else momento.replace(tzinfo=UTC)


def _ultimo_ensayo(db: Session, user_id: int) -> datetime | None:
    return db.execute(
        select(ExamAttempt.finished_at)
        .where(ExamAttempt.user_id == user_id)
        .where(ExamAttempt.status == "submitted")
        .where(ExamAttempt.finished_at.is_not(None))
        .order_by(ExamAttempt.finished_at.desc())
        .limit(1)
    ).scalar_one_or_none()


def _mensaje(
    nombre: str,
    dias_sin_rendir: int,
    racha: int,
    url: str,
    paso: tuple[str, str] | None = None,
    dias_paes: int = 0,
) -> tuple[str, str]:
    """Asunto y cuerpo. Cambia según lo que la persona tenga en juego.

    A quien tiene una racha viva se le nombra lo que está por perder, que es
    concreto. A quien no la tiene no se le inventa una: se le ofrece empezar.
    """
    if racha >= 2:
        asunto = f"{nombre}, llevas {racha} días seguidos"
        cuerpo = (
            f"Hola {nombre}:\n\n"
            f"Llevas {racha} días seguidos rindiendo ensayos. Si hoy no rindes "
            f"ninguno, la racha vuelve a cero.\n\n"
            f"Un ensayo corto son 20 preguntas y unos 40 minutos:\n{url}/examen\n\n"
        )
    elif dias_sin_rendir >= 7:
        asunto = f"{nombre}, hace {dias_sin_rendir} días que no rindes un ensayo"
        cuerpo = (
            f"Hola {nombre}:\n\n"
            f"Hace {dias_sin_rendir} días que no rindes un ensayo. Retomar cuesta "
            f"menos de lo que parece: parte por uno corto, de 20 preguntas.\n\n"
            f"{url}/examen\n\n"
        )
    else:
        asunto = f"{nombre}, ¿rendimos un ensayo hoy?"
        cuerpo = (
            f"Hola {nombre}:\n\n"
            f"Un ensayo corto hoy son 40 minutos, y mantiene tu preparación al "
            f"día.\n\n{url}/examen\n\n"
        )

    if paso:
        titulo, enlace = paso
        cuerpo += f"¿Poco tiempo? 15 minutos en «{titulo}», que es lo que más te conviene reforzar:\n{enlace}\n\n"
    if dias_paes > 0:
        cuerpo += f"Quedan {dias_paes} días para la PAES."

    return asunto, cuerpo.rstrip() + pie_de_baja(url)


def enviar_recordatorios(
    db: Session, limite: int = 200, ahora: datetime | None = None
) -> dict[str, int]:
    """Recorre las cuentas y manda los recordatorios que correspondan.

    Devuelve el recuento para que el cron deje rastro de lo que hizo. Sin SMTP
    configurado en desarrollo, `send_email` deja el mensaje en el log y el
    resultado dice cuántos se habrían mandado — así el sistema se puede probar
    entero antes de contratar un proveedor.

    Un correo que falla NO detiene la tanda: se cuenta aparte y se sigue con
    los demás. Es un recorrido de hasta 200 cuentas, y que una dirección
    rebotada deje sin recordatorio a las otras 199 sería un error caro y
    silencioso. A quien falló no se le marca la fecha, así que entra de nuevo
    en la pasada siguiente.
    """
    ajustes = get_settings()
    ahora = ahora or datetime.now(UTC)
    hoy = ahora.date()
    inicio = time.monotonic()
    dias_paes = max(0, (FECHA_PAES - ahora).days)

    resultado = {"revisados": 0, "enviados": 0, "omitidos": 0, "fallidos": 0}

    # Regla 4: el domingo el único correo es el resumen semanal.
    if ahora.weekday() == DIA_DEL_RESUMEN:
        return resultado

    candidatos = db.execute(
        select(User)
        .where(User.recordatorios_email.is_(True))
        .limit(limite)
    ).scalars().all()

    for user in candidatos:
        if time.monotonic() - inicio > PRESUPUESTO_SEGUNDOS:
            break
        resultado["revisados"] += 1

        # Regla 2: nunca dos días seguidos.
        anterior = _con_zona(user.ultimo_recordatorio)
        if anterior and (ahora - anterior) < timedelta(days=DESCANSO_DIAS):
            resultado["omitidos"] += 1
            continue

        ultimo = _con_zona(_ultimo_ensayo(db, user.id))
        dias_sin_rendir = (hoy - ultimo.date()).days if ultimo else ABANDONO_DIAS

        # Regla 3: ya rindió hoy, o hace tanto que ya no es un recordatorio.
        if dias_sin_rendir == 0 or dias_sin_rendir > ABANDONO_DIAS:
            resultado["omitidos"] += 1
            continue

        # La racha que está en juego: días seguidos hasta ayer.
        racha = 0
        if ultimo is not None:
            fechas = {
                f.date()
                for f in db.execute(
                    select(ExamAttempt.finished_at)
                    .where(ExamAttempt.user_id == user.id)
                    .where(ExamAttempt.status == "submitted")
                    .where(ExamAttempt.finished_at.is_not(None))
                ).scalars().all()
                if f is not None
            }
            cursor = hoy if hoy in fechas else hoy - timedelta(days=1)
            while cursor in fechas:
                racha += 1
                cursor -= timedelta(days=1)

        nombre = user.name.split(" ")[0]
        asunto, cuerpo = _mensaje(
            nombre,
            dias_sin_rendir,
            racha,
            ajustes.frontend_url,
            siguiente_paso(db, user, ajustes.frontend_url),
            dias_paes,
        )
        try:
            send_email(user.email, asunto, cuerpo)
        except CorreoNoEnviado:
            logger.exception("No se pudo enviar el recordatorio a %s", user.email)
            resultado["fallidos"] += 1
            continue

        user.ultimo_recordatorio = ahora
        resultado["enviados"] += 1

    db.commit()
    return resultado
