"""Analítica del estudiante: se calcula al vuelo a partir de ExamAnswer y
PracticeAnswer, en lugar de mantener la tabla study_streaks pre-agregada
(existe en el modelo para cuando el volumen de datos lo justifique; por
ahora recalcular es más simple y siempre consistente con la fuente)."""

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from itertools import pairwise

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.analytics.schemas import AnalyticsSummaryOut, DailyStat
from paes_api.modules.content.models import Alternative
from paes_api.modules.exam_focus.models import ExamAnswer, ExamAttempt
from paes_api.modules.practice.models import PracticeAnswer
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
