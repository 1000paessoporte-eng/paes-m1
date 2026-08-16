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
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.email import send_email
from paes_api.modules.exam_focus.models import ExamAttempt
from paes_api.modules.users.models import User

#: Días mínimos entre dos recordatorios a la misma persona.
DESCANSO_DIAS = 2
#: Sobre esto, la cuenta se considera dormida y se deja de insistir.
ABANDONO_DIAS = 45


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


def _mensaje(nombre: str, dias_sin_rendir: int, racha: int, url: str) -> tuple[str, str]:
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

    cuerpo += (
        "Si no quieres recibir estos recordatorios, puedes apagarlos en tu "
        f"perfil:\n{url}/perfil\n\n— 1000paes"
    )
    return asunto, cuerpo


def enviar_recordatorios(db: Session, limite: int = 200) -> dict[str, int]:
    """Recorre las cuentas y manda los recordatorios que correspondan.

    Devuelve el recuento para que el cron deje rastro de lo que hizo. Sin SMTP
    configurado, `send_email` deja el mensaje en el log y el resultado dice
    cuántos se habrían mandado — así el sistema se puede probar entero antes de
    contratar un proveedor.
    """
    ajustes = get_settings()
    ahora = datetime.now(UTC)
    hoy = ahora.date()

    candidatos = db.execute(
        select(User)
        .where(User.recordatorios_email.is_(True))
        .limit(limite)
    ).scalars().all()

    resultado = {"revisados": 0, "enviados": 0, "omitidos": 0}

    for user in candidatos:
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
        asunto, cuerpo = _mensaje(nombre, dias_sin_rendir, racha, ajustes.frontend_url)
        send_email(user.email, asunto, cuerpo)

        user.ultimo_recordatorio = ahora
        resultado["enviados"] += 1

    db.commit()
    return resultado
