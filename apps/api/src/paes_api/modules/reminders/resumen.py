"""Resumen semanal: "Tu semana en 1000paes".

Sale los domingos en la tarde. El recordatorio le pide algo al alumno ("rinde
un ensayo"); este le devuelve algo: lo que hizo en la semana, si mejoró, y qué
le conviene estudiar ahora. Es el correo que da ganas de abrir los siguientes.

Las reglas son las mismas que ordenan los recordatorios, por la misma razón --un
solo dominio, y si se quema dejan de llegar los de recuperar contraseña--:

1. **Nunca a quien apagó los correos** en su perfil (`recordatorios_email`).
2. **Solo si hay algo que contar.** A quien no ha tocado la plataforma en
   cuatro semanas no se le manda un resumen de nada: ese correo solo enseña a
   ignorar al remitente.
3. **Nunca dos correos el mismo día.** El domingo no sale recordatorio
   (`service.enviar_recordatorios` lo salta), así que este es el único.

Los números salen de las mismas funciones que alimentan `/analitica`, para que
el correo y la pantalla nunca digan cosas distintas.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.email import CorreoNoEnviado, send_email
from paes_api.modules.analytics.service import (
    _compute_streak,
    _daily_buckets,
    _dias_con_ensayo,
)
from paes_api.modules.exam_focus.models import ExamAttempt
from paes_api.modules.goals.service import FACTORES, FECHA_PAES
from paes_api.modules.reminders.service import (
    PRESUPUESTO_SEGUNDOS,
    _con_zona,
    pie_de_baja,
    siguiente_paso,
)
from paes_api.modules.users.models import User

logger = logging.getLogger(__name__)

#: Sin actividad en este lapso, la cuenta no recibe resumen.
INACTIVIDAD_DIAS = 28

ETIQUETAS = {subject: etiqueta for etiqueta, subject in FACTORES.values() if subject}


@dataclass
class Semana:
    preguntas: int = 0
    correctas: int = 0
    dias_activos: int = 0
    ensayos: int = 0
    #: Mejor puntaje de la semana por prueba, y el mejor que tenía antes.
    puntajes: dict[str, tuple[int, int | None]] = field(default_factory=dict)

    @property
    def acierto(self) -> int | None:
        return round(100 * self.correctas / self.preguntas) if self.preguntas else None


def _totales(buckets: dict[date, dict[str, float]], desde: date, hasta: date) -> tuple[int, int, int]:
    """Preguntas, correctas y días con práctica en [desde, hasta)."""
    dias = [b for d, b in buckets.items() if desde <= d < hasta]
    return (
        sum(int(b["answered"]) for b in dias),
        sum(int(b["correct"]) for b in dias),
        sum(1 for b in dias if b["answered"]),
    )


def _puntajes(db: Session, user_id: int, desde: datetime) -> tuple[int, dict[str, tuple[int, int | None]]]:
    """Ensayos terminados en la semana y, por prueba, el mejor de la semana
    contra el mejor de antes. Solo cuentan los ensayos representativos: los
    contestados sin leer no dicen nada de lo que la persona sabe."""
    filas = db.execute(
        select(ExamAttempt.subject, ExamAttempt.estimated_score, ExamAttempt.finished_at)
        .where(ExamAttempt.user_id == user_id)
        .where(ExamAttempt.status == "submitted")
        .where(ExamAttempt.finished_at.is_not(None))
        .where(ExamAttempt.estimated_score.is_not(None))
        .where(ExamAttempt.representativo.is_(True))
    ).all()

    ensayos = 0
    semana: dict[str, int] = {}
    antes: dict[str, int] = {}
    for subject, puntaje, fin in filas:
        fin = _con_zona(fin)
        destino = semana if fin >= desde else antes
        if fin >= desde:
            ensayos += 1
        destino[subject] = max(destino.get(subject, 0), puntaje)

    return ensayos, {s: (p, antes.get(s)) for s, p in semana.items()}


def resumir(db: Session, user: User, ahora: datetime) -> tuple[Semana, Semana, set[date]]:
    """Esta semana, la anterior, y todos los días con actividad (respuestas
    sueltas o ensayos terminados)."""
    buckets = _daily_buckets(db, user)
    hoy = ahora.date()
    inicio = hoy - timedelta(days=6)

    esta = Semana()
    esta.preguntas, esta.correctas, esta.dias_activos = _totales(buckets, inicio, hoy + timedelta(days=1))
    esta.ensayos, esta.puntajes = _puntajes(
        db, user.id, datetime.combine(inicio, datetime.min.time(), tzinfo=UTC)
    )

    previa = Semana()
    previa.preguntas, previa.correctas, previa.dias_activos = _totales(
        buckets, inicio - timedelta(days=7), inicio
    )
    activos = {d for d, b in buckets.items() if b["answered"]} | _dias_con_ensayo(db, user)
    return esta, previa, activos


def _comparar(actual: int, anterior: int) -> str:
    if not anterior:
        return ""
    if actual > anterior:
        return f" (la semana pasada fueron {anterior}: vas en subida)"
    if actual < anterior:
        return f" (la semana pasada fueron {anterior})"
    return " (igual que la semana pasada)"


def mensaje(
    nombre: str,
    esta: Semana,
    previa: Semana,
    racha: int,
    paso: tuple[str, str] | None,
    dias_paes: int,
    url: str,
) -> tuple[str, str]:
    """Asunto y cuerpo. Dos versiones: la de quien practicó y la de quien no.

    A quien no practicó no se le reprocha: se le recuerda lo que llevaba y se
    le ofrece un paso chico. El reproche es lo que hace que la gente apague los
    correos.
    """
    lineas: list[str] = [f"Hola {nombre}:", ""]

    if esta.preguntas:
        asunto = f"{nombre}, tu semana: {esta.preguntas} preguntas"
        if esta.acierto is not None:
            asunto += f" y {esta.acierto}% de acierto"
        lineas += [
            "Esto es lo que hiciste en los últimos 7 días:",
            "",
            f"• {esta.preguntas} preguntas respondidas{_comparar(esta.preguntas, previa.preguntas)}",
        ]
        if esta.acierto is not None:
            linea = f"• {esta.acierto}% de acierto"
            if previa.acierto is not None and previa.acierto != esta.acierto:
                linea += f" (la semana pasada {previa.acierto}%)"
            lineas.append(linea)
        lineas.append(f"• Estudiaste {esta.dias_activos} de 7 días")
        if esta.ensayos:
            lineas.append(f"• {esta.ensayos} ensayo{'s' if esta.ensayos != 1 else ''} terminado{'s' if esta.ensayos != 1 else ''}")
        if racha >= 2:
            lineas.append(f"• Llevas {racha} días seguidos practicando")

        if esta.puntajes:
            lineas += ["", "Tu mejor puntaje de la semana:"]
            for subject, (mejor, antes) in sorted(esta.puntajes.items()):
                etiqueta = ETIQUETAS.get(subject, subject)
                if antes is None:
                    extra = " (tu primer puntaje en esta prueba)"
                elif mejor > antes:
                    extra = f" (¡nuevo récord! antes {antes})"
                else:
                    extra = f" (tu récord sigue en {antes})"
                lineas.append(f"• {etiqueta}: {mejor}{extra}")
    else:
        asunto = f"{nombre}, esta semana no alcanzaste a practicar"
        lineas.append(
            "Pasa. Lo importante es no "
            "soltar el ritmo por más de una semana."
        )
        if previa.preguntas:
            lineas.append(
                f"La semana anterior respondiste {previa.preguntas} preguntas. "
                "Con 15 minutos hoy retomas."
            )

    lineas.append("")
    if paso:
        titulo, enlace = paso
        lineas += [f"Lo que más te conviene ahora: {titulo}", enlace, ""]
    else:
        lineas += [f"Para seguir, un ensayo corto de 20 preguntas:\n{url}/examen", ""]

    if dias_paes > 0:
        lineas.append(f"Quedan {dias_paes} días para la PAES.")
        lineas.append("")

    lineas.append(f"Tu avance completo: {url}/analitica")
    cuerpo = "\n".join(lineas) + pie_de_baja(url)
    return asunto, cuerpo


def enviar_resumenes(
    db: Session, limite: int = 500, ahora: datetime | None = None
) -> dict[str, int]:
    """Manda el resumen semanal a quien corresponda. La llama el cron del domingo.

    Corta al llegar a `PRESUPUESTO_SEGUNDOS`: la función muere a los 30 s y un
    corte a la fuerza no dejaría ni el recuento. Quien quede fuera se cuenta en
    `pendientes`; con el volumen actual no debería pasar, y si pasa el número
    lo muestra antes de que sea un problema.
    """
    ajustes = get_settings()
    ahora = ahora or datetime.now(UTC)
    inicio = time.monotonic()
    dias_paes = max(0, (FECHA_PAES - ahora).days)

    cuentas = db.execute(
        select(User).where(User.recordatorios_email.is_(True)).order_by(User.id).limit(limite)
    ).scalars().all()

    resultado = {"revisados": 0, "enviados": 0, "omitidos": 0, "fallidos": 0, "pendientes": 0}

    for user in cuentas:
        if time.monotonic() - inicio > PRESUPUESTO_SEGUNDOS:
            resultado["pendientes"] += 1
            continue
        resultado["revisados"] += 1

        esta, previa, activos = resumir(db, user, ahora)
        ultimo = max(activos) if activos else None
        creada = _con_zona(user.created_at)
        reciente = creada is not None and (ahora - creada).days < 14

        # Regla 2: solo si hay algo que contar.
        if (ultimo is None or (ahora.date() - ultimo).days > INACTIVIDAD_DIAS) and not reciente:
            resultado["omitidos"] += 1
            continue

        nombre = user.name.split(" ")[0] if user.name else "Hola"
        asunto, cuerpo = mensaje(
            nombre,
            esta,
            previa,
            _compute_streak(activos),
            siguiente_paso(db, user, ajustes.frontend_url),
            dias_paes,
            ajustes.frontend_url,
        )
        try:
            send_email(user.email, asunto, cuerpo)
        except CorreoNoEnviado:
            logger.exception("No se pudo enviar el resumen semanal a %s", user.email)
            resultado["fallidos"] += 1
            continue
        resultado["enviados"] += 1

    logger.warning("Resumen semanal: %s", resultado)
    return resultado
