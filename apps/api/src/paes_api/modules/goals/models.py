"""La meta del estudiante: a qué carrera quiere entrar y cuánto le falta.

En Chile nadie estudia para "subir el puntaje". Se estudia para entrar a una
carrera, y el puntaje que importa no es el de una prueba sino el PONDERADO, que
combina NEM, ranking y las pruebas con los pesos que fija cada carrera. Una
misma persona puede estar sobrada para una carrera y lejos de otra con
exactamente los mismos puntajes.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from paes_api.shared.base import Base

if TYPE_CHECKING:
    from paes_api.modules.users.models import User


class Carrera(Base):
    """Una carrera con sus ponderaciones oficiales.

    Los datos salen del PDF de oferta definitiva del DEMRE y se cargan con
    `scripts/extraer_carreras.py`, que descarta cualquier carrera cuyas
    ponderaciones no sumen 100. `proceso` y `fuente` viajan con el dato porque
    las ponderaciones cambian cada año y la pantalla tiene que poder decir de
    dónde salió el número.
    """

    __tablename__ = "carreras"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(10), index=True)
    universidad: Mapped[str] = mapped_column(String(200), index=True)
    nombre: Mapped[str] = mapped_column(String(250), index=True)
    sede: Mapped[str] = mapped_column(String(120))

    #: Ponderaciones en porcentaje. Suman 100 entre todas.
    nem: Mapped[float | None] = mapped_column(Float, nullable=True)
    ranking: Mapped[float | None] = mapped_column(Float, nullable=True)
    lectora: Mapped[float | None] = mapped_column(Float, nullable=True)
    m1: Mapped[float | None] = mapped_column(Float, nullable=True)
    historia: Mapped[float | None] = mapped_column(Float, nullable=True)
    ciencias: Mapped[float | None] = mapped_column(Float, nullable=True)
    m2: Mapped[float | None] = mapped_column(Float, nullable=True)
    prueba_especial: Mapped[float | None] = mapped_column(Float, nullable=True)

    #: Cuando la carrera acepta "Historia ó Ciencias", ambas traen el mismo peso
    #: pero solo cuenta la mejor de las dos.
    electivo_alternativo: Mapped[bool] = mapped_column(Boolean, default=False)

    proceso: Mapped[int] = mapped_column(Integer)
    fuente: Mapped[str] = mapped_column(String(300))

    metas: Mapped[list["MetaUsuario"]] = relationship(back_populates="carrera")


class MetaUsuario(Base):
    """La carrera que el estudiante persigue, con sus datos de colegio.

    NEM y ranking se guardan como PUNTAJE (100-1000) y no como promedio de
    notas: la conversión de notas a puntaje la hace el DEMRE con una tabla que
    depende de la generación, así que calcularla acá sería inventar. El
    estudiante los copia de su informe, o los deja en blanco y ve la proyección
    solo con lo que sí sabemos.
    """

    __tablename__ = "user_goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    carrera_id: Mapped[int] = mapped_column(ForeignKey("carreras.id"), index=True)

    puntaje_nem: Mapped[int | None] = mapped_column(Integer, nullable=True)
    puntaje_ranking: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship(back_populates="goal")
    carrera: Mapped["Carrera"] = relationship(back_populates="metas")
