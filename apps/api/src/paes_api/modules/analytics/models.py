from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from paes_api.shared.base import Base


class StudyStreak(Base):
    """Una fila por (usuario, día) — base de las rachas y del gráfico
    tiempo invertido vs. tasa de acierto en el Dashboard Analítico."""

    __tablename__ = "study_streaks"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_user_day"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    day: Mapped[date] = mapped_column(Date)
    questions_answered: Mapped[int] = mapped_column(Integer, default=0)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    minutes_practiced: Mapped[int] = mapped_column(Integer, default=0)
