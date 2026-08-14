from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from paes_api.shared.base import Base

if TYPE_CHECKING:
    from paes_api.modules.content.models import Question
    from paes_api.modules.users.models import User


class SkillAxis(StrEnum):
    """Dimensión del temario a la que pertenece un nodo.

    En matemática son los cuatro ejes temáticos del DEMRE. En Competencia
    Lectora no hay ejes de contenido: la prueba se organiza por las tres
    habilidades que declara el temario (localizar, interpretar y evaluar), y
    son esas las que ocupan el lugar del eje.
    """

    NUMEROS = "numeros"
    ALGEBRA = "algebra"
    GEOMETRIA = "geometria"
    PROBABILIDAD = "probabilidad"
    # Competencia Lectora
    LOCALIZAR = "localizar"
    INTERPRETAR = "interpretar"
    EVALUAR = "evaluar"
    # Ciencias
    BIOLOGIA = "biologia"
    FISICA = "fisica"
    QUIMICA = "quimica"
    # Historia y Ciencias Sociales
    HISTORIA = "historia"
    CIUDADANIA = "ciudadania"
    ECONOMIA = "economia"


class Subject(StrEnum):
    """Prueba PAES a la que pertenece un nodo. M2 evalúa "todos los
    conocimientos de M1, además de" contenido propio (ver temario DEMRE), por
    eso M2 no duplica los nodos de M1: los reutiliza y solo agrega los nodos
    exclusivos de M2. `exam_focus.service.SUBJECT_INCLUDES` es la fuente de
    verdad de qué subjects entran al banco de preguntas de cada prueba."""

    M1 = "m1"
    M2 = "m2"
    LECTORA = "lectora"
    CIENCIAS = "ciencias"
    HISTORIA = "historia"


class ProgressStatus(StrEnum):
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    MASTERED = "mastered"


# Un nodo puede requerir varios nodos previos (grafo, no solo árbol binario).
skill_prerequisites = Table(
    "skill_prerequisites",
    Base.metadata,
    Column("skill_node_id", ForeignKey("skill_nodes.id"), primary_key=True),
    Column("prerequisite_id", ForeignKey("skill_nodes.id"), primary_key=True),
)


class SkillNode(Base):
    """Nodo del Árbol de Habilidades. `unlock_threshold` es el % de acierto
    mínimo exigido en TODOS los prerequisites para desbloquear este nodo."""

    __tablename__ = "skill_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    axis: Mapped[SkillAxis] = mapped_column(Enum(SkillAxis))
    subject: Mapped[Subject] = mapped_column(
        Enum(Subject), default=Subject.M1, server_default=Subject.M1.name
    )
    tier: Mapped[int] = mapped_column(Integer, default=1)  # nivel/profundidad en el árbol
    unlock_threshold: Mapped[float] = mapped_column(Float, default=0.75)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    prerequisites: Mapped[list["SkillNode"]] = relationship(
        "SkillNode",
        secondary=skill_prerequisites,
        primaryjoin=id == skill_prerequisites.c.skill_node_id,
        secondaryjoin=id == skill_prerequisites.c.prerequisite_id,
    )
    questions: Mapped[list["Question"]] = relationship(back_populates="skill_node")
    user_progress: Mapped[list["UserSkillProgress"]] = relationship(
        back_populates="skill_node"
    )


class UserSkillProgress(Base):
    """Progreso independiente por (usuario, nodo) — el corazón del loop de
    juego: cada intento actualiza accuracy y puede desbloquear nodos hijos."""

    __tablename__ = "user_skill_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    skill_node_id: Mapped[int] = mapped_column(ForeignKey("skill_nodes.id"), index=True)

    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus), default=ProgressStatus.LOCKED
    )
    unlocked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    mastered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="skill_progress")
    skill_node: Mapped["SkillNode"] = relationship(back_populates="user_progress")

    @property
    def accuracy(self) -> float:
        return self.correct / self.attempts if self.attempts else 0.0
