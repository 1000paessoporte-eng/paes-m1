from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from paes_api.shared.base import Base


class Difficulty(StrEnum):
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    skill_node_id: Mapped[int] = mapped_column(ForeignKey("skill_nodes.id"), index=True)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty))
    stem: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    skill_node: Mapped["SkillNode"] = relationship(back_populates="questions")
    alternatives: Mapped[list["Alternative"]] = relationship(
        back_populates="question", order_by="Alternative.label"
    )


class Alternative(Base):
    """Cada alternativa incorrecta DEBE traer distractor_justification:
    el error conceptual exacto que induce a elegirla (base del Smart
    Feedback / autopsia del error)."""

    __tablename__ = "alternatives"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    label: Mapped[str] = mapped_column(String(1))  # "A".."E"
    text: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    distractor_justification: Mapped[str | None] = mapped_column(Text, nullable=True)

    question: Mapped["Question"] = relationship(back_populates="alternatives")
