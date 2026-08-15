from datetime import date

from pydantic import BaseModel


class DailyStat(BaseModel):
    date: date
    questions_answered: int
    correct: int
    accuracy: float | None
    minutes_practiced: float


class AnalyticsSummaryOut(BaseModel):
    current_streak_days: int
    #: Días distintos con al menos 10 preguntas respondidas, en todo el
    #: historial. Es el criterio de constancia que exigen las bases del premio,
    #: y la serie `daily` no sirve para eso: solo cubre las últimas dos semanas.
    active_days: int = 0
    total_questions_answered: int
    total_correct: int
    overall_accuracy: float | None
    total_minutes_practiced: float
    daily: list[DailyStat]
