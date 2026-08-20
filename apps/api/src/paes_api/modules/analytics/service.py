"""Analítica del estudiante: se calcula al vuelo a partir de ExamAnswer y
PracticeAnswer, en lugar de mantener la tabla study_streaks pre-agregada
(existe en el modelo para cuando el volumen de datos lo justifique; por
ahora recalcular es más simple y siempre consistente con la fuente)."""

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from itertools import pairwise

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.analytics.schemas import (
    AnalyticsSummaryOut,
    DailyStat,
    DiagnosticoOut,
    ErrorRepetido,
    RitmoEje,
    RitmoOut,
)
from paes_api.modules.content.models import Alternative, Question
from paes_api.modules.exam_focus.models import ExamAnswer, ExamAttempt
from paes_api.modules.exam_focus.scoring import (
    SCORING_BY_SUBJECT,
    segundos_por_pregunta,
)
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.skill_tree.models import AXIS_LABELS, SkillNode
from paes_api.modules.users.models import User

CHART_DAYS = 14


def _daily_buckets(db: Session, user: User) -> dict[date, dict[str, float]]:
    """Combina Modo Ensayo y Modo Práctica. Solo el ensayo trae tiempo por
    respuesta (time_spent_ms autoguardado durante el intento); la práctica no
    mide tiempo por pregunta, así que solo aporta a "answered"/"correct" y,
    por lo tanto, a la racha y la precisión — no a los minutos practicados."""
    exam_rows = db.execute(
        select(ExamAnswer, Alternative.is_correct)
        .join(ExamAttempt, ExamAnswer.attempt_id == ExamAttempt.id)
        .outerjoin(Alternative, ExamAnswer.selected_alternative_id == Alternative.id)
        .where(ExamAttempt.user_id == user.id, ExamAnswer.answered_at.is_not(None))
    ).all()

    buckets: dict[date, dict[str, float]] = defaultdict(
        lambda: {"answered": 0, "correct": 0, "ms": 0}
    )
    for answer, is_correct in exam_rows:
        d = answer.answered_at.date()
        b = buckets[d]
        b["answered"] += 1
        if is_correct:
            b["correct"] += 1
        b["ms"] += answer.time_spent_ms or 0

    practice_rows = db.execute(
        select(PracticeAnswer.answered_at, PracticeAnswer.is_correct).where(
            PracticeAnswer.user_id == user.id
        )
    ).all()
    for answered_at, is_correct in practice_rows:
        d = answered_at.date()
        b = buckets[d]
        b["answered"] += 1
        if is_correct:
            b["correct"] += 1

    return buckets


def _compute_streak(active_dates: set[date]) -> int:
    if not active_dates:
        return 0
    today = datetime.now(UTC).date()
    cursor = today if today in active_dates else today - timedelta(days=1)
    streak = 0
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _dias_con_ensayo(db: Session, user: User) -> set[date]:
    """Días en que el estudiante TERMINÓ al menos un ensayo.

    Distinto de los días con actividad: responder tres preguntas sueltas no es
    lo mismo que sentarse a rendir. Esta es la racha que se muestra como logro
    y la que exige el premio.
    """
    filas = db.execute(
        select(ExamAttempt.finished_at)
        .where(ExamAttempt.user_id == user.id)
        .where(ExamAttempt.status == "submitted")
        .where(ExamAttempt.finished_at.is_not(None))
    ).scalars().all()
    return {f.date() for f in filas if f is not None}


def _mejor_racha(fechas: set[date]) -> int:
    """El tramo consecutivo más largo, no el actual.

    Es lo que se usa para el premio a propósito: la racha actual castiga para
    siempre a quien se enfermó un martes, y eso no mide constancia, mide suerte.
    El mejor tramo sí premia haber sostenido el hábito.
    """
    if not fechas:
        return 0
    ordenadas = sorted(fechas)
    mejor = actual = 1
    for previa, siguiente in pairwise(ordenadas):
        actual = actual + 1 if (siguiente - previa).days == 1 else 1
        mejor = max(mejor, actual)
    return mejor


def get_summary(db: Session, user: User) -> AnalyticsSummaryOut:
    buckets = _daily_buckets(db, user)

    total_answered = sum(int(b["answered"]) for b in buckets.values())
    total_correct = sum(int(b["correct"]) for b in buckets.values())
    total_ms = sum(b["ms"] for b in buckets.values())

    streak = _compute_streak(set(buckets.keys()))

    # Un día "con práctica" son 10 preguntas o más: abrir la aplicación y
    # responder una no es haber practicado ese día.
    active_days = sum(1 for b in buckets.values() if int(b["answered"]) >= 10)

    dias_ensayo = _dias_con_ensayo(db, user)
    exam_streak = _compute_streak(dias_ensayo)
    best_exam_streak = _mejor_racha(dias_ensayo)

    since = datetime.now(UTC).date() - timedelta(days=CHART_DAYS - 1)
    daily: list[DailyStat] = []
    for i in range(CHART_DAYS):
        d = since + timedelta(days=i)
        b = buckets.get(d, {"answered": 0, "correct": 0, "ms": 0})
        answered = int(b["answered"])
        daily.append(
            DailyStat(
                date=d,
                questions_answered=answered,
                correct=int(b["correct"]),
                accuracy=(b["correct"] / answered) if answered else None,
                minutes_practiced=round(b["ms"] / 60000, 1),
            )
        )

    return AnalyticsSummaryOut(
        current_streak_days=streak,
        active_days=active_days,
        exam_streak_days=exam_streak,
        best_exam_streak_days=best_exam_streak,
        exam_days=len(dias_ensayo),
        total_questions_answered=total_answered,
        total_correct=total_correct,
        overall_accuracy=(total_correct / total_answered) if total_answered else None,
        total_minutes_practiced=round(total_ms / 60000, 1),
        daily=daily,
    )


#: Cuántos errores se muestran. Corto a propósito: una lista de treinta cosas
#: que arreglar no se arregla, se cierra.
MAX_ERRORES = 6

#: Cuántas respuestas con tiempo medido hacen falta antes de hablar de ritmo.
#: Con menos, el promedio lo mueve una sola pregunta en la que se distrajo, y
#: proyectar sobre eso sería inventar. Ya pasó en este proyecto: extrapolar
#: cuatro ensayos del mismo día daba -2.760 puntos al mes.
MIN_RESPUESTAS_RITMO = 20

#: Lo mismo por eje: el desglose es más fino, así que exige menos, pero exige.
MIN_RESPUESTAS_EJE = 5


def errores_repetidos(db: Session, user: User, limite: int = MAX_ERRORES) -> list[ErrorRepetido]:
    """Los errores de razonamiento que cometió el alumno, el más frecuente primero.

    El valor está en MOSTRARLOS: el texto que explica por qué cada alternativa
    incorrecta atrae --"invirtió la división", "se quedó en el paso intermedio
    sin dividir por 2"-- está escrito para las 5.586 alternativas del banco y no
    aparecía en ninguna pantalla. Toda plataforma dice cuál era la correcta;
    esta dice por qué la cabeza fue hacia la otra.

    Se agrupa por el texto para poder decir "esto te pasó tres veces", pero NO
    se exige repetición para mostrarlo. Se midió sobre el banco real: 5.586
    distractores tienen 5.284 textos distintos, así que exigir dos apariciones
    dejaba la sección vacía casi siempre. La repetición es un agravante que se
    señala cuando ocurre, no el requisito para hablar.
    """
    filas = db.execute(
        select(
            Alternative.distractor_justification,
            Question.stem,
            SkillNode.code,
            SkillNode.name,
            SkillNode.axis,
        )
        .select_from(ExamAnswer)
        .join(ExamAttempt, ExamAttempt.id == ExamAnswer.attempt_id)
        .join(Alternative, Alternative.id == ExamAnswer.selected_alternative_id)
        .join(Question, Question.id == ExamAnswer.question_id)
        .join(SkillNode, SkillNode.id == Question.skill_node_id)
        .where(
            ExamAttempt.user_id == user.id,
            Alternative.is_correct.is_(False),
            Alternative.distractor_justification.is_not(None),
            Alternative.distractor_justification != "",
        )
    ).all()

    conteo: dict[str, dict] = {}
    for texto, stem, code, name, axis in filas:
        clave = texto.strip()
        fila = conteo.setdefault(
            clave,
            {"veces": 0, "stem": stem, "code": code, "name": name, "axis": axis},
        )
        fila["veces"] += 1

    errores = [
        ErrorRepetido(
            descripcion=texto,
            pregunta=d["stem"],
            veces=d["veces"],
            node_code=d["code"],
            node_name=d["name"],
            axis_label=AXIS_LABELS.get(d["axis"].value, d["axis"].value),
        )
        for texto, d in conteo.items()
    ]
    # Lo que más se repite primero: si algo le pasó tres veces, es lo que tiene
    # que arreglar antes que un tropiezo suelto.
    errores.sort(key=lambda e: -e.veces)
    return errores[:limite]


def ritmo(db: Session, user: User) -> RitmoOut | None:
    """Cuánto se demora el alumno por pregunta, contra lo que da la prueba.

    Solo cuenta respuestas con tiempo medido y con una alternativa elegida: una
    pregunta que se saltó no dice nada sobre el ritmo.

    Devuelve None cuando no hay datos suficientes. Es a propósito: una pantalla
    que dice "vas lento" apoyada en tres respuestas es peor que no decir nada.
    """
    filas = db.execute(
        select(ExamAnswer.time_spent_ms, SkillNode.axis, ExamAttempt.subject)
        .select_from(ExamAnswer)
        .join(ExamAttempt, ExamAttempt.id == ExamAnswer.attempt_id)
        .join(Question, Question.id == ExamAnswer.question_id)
        .join(SkillNode, SkillNode.id == Question.skill_node_id)
        .where(
            ExamAttempt.user_id == user.id,
            ExamAnswer.time_spent_ms > 0,
            ExamAnswer.selected_alternative_id.is_not(None),
        )
    ).all()

    if len(filas) < MIN_RESPUESTAS_RITMO:
        return None

    por_eje: dict[str, list[int]] = defaultdict(list)
    for ms, axis, _subject in filas:
        por_eje[AXIS_LABELS.get(axis.value, axis.value)].append(ms)

    # La prueba de referencia es la que más ha rendido: comparar su ritmo
    # contra el de una prueba que casi no toca no le sirve de nada.
    conteo_subject: dict = defaultdict(int)
    for _ms, _axis, subject in filas:
        conteo_subject[subject] += 1
    subject_ref = max(conteo_subject, key=lambda s: conteo_subject[s])
    oficiales = segundos_por_pregunta(subject_ref)

    total_ms = sum(ms for ms, _a, _s in filas)
    segundos_alumno = total_ms / len(filas) / 1000

    ejes = [
        RitmoEje(
            axis_label=etiqueta,
            segundos_por_pregunta=round(sum(v) / len(v) / 1000, 1),
            respuestas=len(v),
        )
        for etiqueta, v in por_eje.items()
        if len(v) >= MIN_RESPUESTAS_EJE
    ]
    ejes.sort(key=lambda e: -e.segundos_por_pregunta)

    # Cuántas quedarían fuera si rindiera la prueba completa a este ritmo.
    total_oficial = SCORING_BY_SUBJECT[subject_ref].preguntas_oficiales
    sin_alcanzar = None
    if total_oficial:
        alcanza = (oficiales * total_oficial) / segundos_alumno
        sin_alcanzar = max(0, round(total_oficial - alcanza))

    return RitmoOut(
        segundos_oficiales=round(oficiales, 1),
        segundos_alumno=round(segundos_alumno, 1),
        por_eje=ejes,
        preguntas_sin_alcanzar=sin_alcanzar,
        respuestas_medidas=len(filas),
    )


def diagnostico(db: Session, user: User) -> DiagnosticoOut:
    return DiagnosticoOut(errores=errores_repetidos(db, user), ritmo=ritmo(db, user))
