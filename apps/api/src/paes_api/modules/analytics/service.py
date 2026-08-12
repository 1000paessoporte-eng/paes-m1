"""Analítica del estudiante: se calcula al vuelo a partir de ExamAnswer,
en lugar de mantener la tabla study_streaks pre-agregada (existe en el
modelo para cuando el volumen de datos lo justifique; por ahora
recalcular es más simple y siempre consistente con la fuente)."""

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.analytics.schemas import AnalyticsSummaryOut, DailyStat
from paes_api.modules.content.models import Alternative
from paes_api.modules.exam_focus.models import ExamAnswer, ExamAttempt
from paes_api.modules.users.models import User

CHART_DAYS = 14


def _daily_buckets(db: Session, user: User) -> dict[date, dict[str, float]]:
    rows = db.execute(
        select(ExamAnswer, Alternative.is_correct)
        .join(ExamAttempt, ExamAnswer.attempt_id == ExamAttempt.id)
        .outerjoin(Alternative, ExamAnswer.selected_alternative_id == Alternative.id)
        .where(ExamAttempt.user_id == user.id, ExamAnswer.answered_at.is_not(None))
    ).all()

    buckets: dict[date, dict[str, float]] = defaultdict(
        lambda: {"answered": 0, "correct": 0, "ms": 0}
    )
    for answer, is_correct in rows:
        d = answer.answered_at.date()
        b = buckets[d]
        b["answered"] += 1
        if is_correct:
            b["correct"] += 1
        b["ms"] += answer.time_spent_ms or 0
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


def get_summary(db: Session, user: User) -> AnalyticsSummaryOut:
    buckets = _daily_buckets(db, user)

    total_answered = sum(int(b["answered"]) for b in buckets.values())
    total_correct = sum(int(b["correct"]) for b in buckets.values())
    total_ms = sum(b["ms"] for b in buckets.values())

    streak = _compute_streak(set(buckets.keys()))

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
        total_questions_answered=total_answered,
        total_correct=total_correct,
        overall_accuracy=(total_correct / total_answered) if total_answered else None,
        total_minutes_practiced=round(total_ms / 60000, 1),
        daily=daily,
    )
