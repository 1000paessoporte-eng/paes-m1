from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from paes_api.shared.base import Base

if TYPE_CHECKING:
    from paes_api.modules.skill_tree.models import SkillNode


class Difficulty(StrEnum):
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class ReadingPassage(Base):
    """Texto base de Competencia Lectora, compartido por varias preguntas.

    La PAES de Competencia Lectora son 8 textos con 65 preguntas asociadas: la
    pregunta sola no se entiende sin el texto. Por eso el pasaje es su propia
    entidad y no un campo de `Question`, que se duplicaría en cada una.

    Los textos son originales del proyecto. No se reproducen los del DEMRE:
    tienen derechos de la Universidad de Chile, y además un texto propio hace
    verificable la respuesta, porque está contenida en lo que escribimos.
    """

    __tablename__ = "reading_passages"

    id: Mapped[int] = mapped_column(primary_key=True)
    #: Título visible sobre el texto.
    title: Mapped[str] = mapped_column(String(200))
    #: Cuerpo del texto. Puede traer saltos de línea y párrafos.
    body: Mapped[str] = mapped_column(Text)
    #: "literario" | "no_literario" | "discontinuo". El temario 2027 sumó peso a
    #: los discontinuos (infografías, tablas), por eso son una categoría propia.
    kind: Mapped[str] = mapped_column(String(20), default="no_literario")
    #: De dónde sale el texto. Para los propios: "Texto original de 1000paes".
    source_note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    questions: Mapped[list["Question"]] = relationship(back_populates="passage")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    skill_node_id: Mapped[int] = mapped_column(ForeignKey("skill_nodes.id"), index=True)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty))
    stem: Mapped[str] = mapped_column(Text)
    #: Desarrollo paso a paso de por qué la respuesta correcta lo es. Nunca
    #: menciona letras de alternativa: el orden A-D se mezcla al sembrar.
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    #: Texto base, solo en Competencia Lectora. NULL en matemática.
    passage_id: Mapped[int | None] = mapped_column(
        ForeignKey("reading_passages.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    skill_node: Mapped["SkillNode"] = relationship(back_populates="questions")
    passage: Mapped["ReadingPassage | None"] = relationship(back_populates="questions")
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
