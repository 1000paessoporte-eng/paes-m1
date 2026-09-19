"""El ensayo del día: lo que rinde el plan Gratis.

Cada día hay un ensayo por prueba, el mismo para todos los alumnos. El plan
Gratis rinde ese, uno por prueba al día; Pro lo puede rendir también, además
de armar los suyos.

Por qué así y no "4 ensayos al mes":

- **Se entiende de un vistazo.** "Hoy te toca este, mañana hay otro" no pide
  llevar la cuenta de cuántos quedan en el mes.
- **Crea hábito.** Un tope mensual se gasta el primer fin de semana y deja al
  alumno tres semanas sin ensayar; uno diario lo trae de vuelta cada día.
- **Es el mismo para todos**, así que se puede comparar con el compañero de
  curso: "¿cuánto te sacaste en el de hoy?".

Sin columna nueva en la base: el ensayo del día se reconoce por su fecha (día
de Chile) y su prueba. Una migración en esta base ya tumbó el login dos veces.
Para el plan Gratis cualquier ensayo empezado hoy en una prueba ES el del día,
porque es el único que puede rendir.

La selección es determinística: misma fecha y misma prueba dan las mismas
preguntas, en cualquier servidor, sin guardarla. Si el banco cambia durante el
día (un `seed.py` en producción), los que lo rindan después pueden recibir un
set distinto. Es raro y no rompe nada: cada intento guarda sus preguntas.
"""

import hashlib
import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.content.models import Question
from paes_api.modules.exam_focus import service
from paes_api.modules.exam_focus.models import AttemptStatus, ExamAttempt, Pace
from paes_api.modules.skill_tree.models import Subject

CHILE = ZoneInfo("America/Santiago")

#: Veinte preguntas: unos 40 minutos en matemática, lo que cabe en una tarde
#: de colegio. Es el mismo formato que el "ensayo corto" que se recomienda
#: para empezar.
PREGUNTAS = 20

PRUEBAS: tuple[Subject, ...] = (
    Subject.LECTORA,
    Subject.M1,
    Subject.M2,
    Subject.HISTORIA,
    Subject.CIENCIAS,
)


def hoy(ahora: datetime | None = None) -> date:
    """El día en Chile. El ensayo cambia a medianoche de Santiago, no de UTC:
    a las 21:00 de Chile ya es mañana en UTC."""
    return (ahora or datetime.now(UTC)).astimezone(CHILE).date()


def _limites_del_dia(fecha: date) -> tuple[datetime, datetime]:
    inicio = datetime.combine(fecha, datetime.min.time(), tzinfo=CHILE)
    return inicio.astimezone(UTC), (inicio + timedelta(days=1)).astimezone(UTC)


def _semilla(fecha: date, subject: Subject) -> int:
    # Un hash y no `hash()`: el de Python cambia entre procesos.
    digest = hashlib.sha256(f"1000paes:{fecha.isoformat()}:{subject.value}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def preguntas_del_dia(db: Session, subject: Subject, fecha: date) -> list[Question]:
    """Las preguntas del ensayo del día. Mismas entradas, mismo resultado.

    Usa el mismo armador que cualquier ensayo --reparto por eje, textos de
    Lectora, cuota de suficiencia de datos-- con el azar sembrado por la fecha
    y sin el historial del alumno: si dependiera de lo que cada uno rindió
    antes, ya no sería el mismo para todos.
    """
    token = service.AZAR.set(random.Random(_semilla(fecha, subject)))
    try:
        pool = service._all_questions(db, subject)
        return service._select_questions(pool, [], PREGUNTAS, subject, None, None, None)
    finally:
        service.AZAR.reset(token)


def intento_de_hoy(
    db: Session, user_id: int, subject: Subject, fecha: date
) -> ExamAttempt | None:
    """El ensayo de esa prueba que el alumno empezó ese día, si hay."""
    desde, hasta = _limites_del_dia(fecha)
    return db.execute(
        select(ExamAttempt)
        .where(ExamAttempt.user_id == user_id)
        .where(ExamAttempt.subject == subject)
        .where(ExamAttempt.started_at >= desde)
        .where(ExamAttempt.started_at < hasta)
        .order_by(ExamAttempt.started_at.desc())
        .limit(1)
    ).scalar_one_or_none()


@dataclass(frozen=True)
class EstadoPrueba:
    subject: Subject
    estado: str  # "disponible" | "en_curso" | "rendido"
    attempt_id: int | None
    puntaje: int | None


def estado(db: Session, user_id: int, fecha: date) -> list[EstadoPrueba]:
    """Cómo va el alumno con el ensayo del día de cada prueba."""
    salida = []
    for subject in PRUEBAS:
        intento = intento_de_hoy(db, user_id, subject, fecha)
        if intento is None:
            salida.append(EstadoPrueba(subject, "disponible", None, None))
        elif intento.status is AttemptStatus.IN_PROGRESS:
            salida.append(EstadoPrueba(subject, "en_curso", intento.id, None))
        else:
            salida.append(EstadoPrueba(subject, "rendido", intento.id, intento.estimated_score))
    return salida


def duracion(subject: Subject) -> int:
    return service.duration_for(PREGUNTAS, Pace.OFICIAL, subject)
