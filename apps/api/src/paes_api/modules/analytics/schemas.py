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
    total_questions_answered: int
    total_correct: int
    overall_accuracy: float | None
    total_minutes_practiced: float
    daily: list[DailyStat]
