"""La meta del estudiante: a qué carrera quiere entrar y cuánto le falta.

En Chile nadie estudia para "subir el puntaje". Se estudia para entrar a una
carrera, y el puntaje que importa no es el de una prueba sino el PONDERADO, que
combina NEM, ranking y las pruebas con los pesos que fija cada carrera. Una
misma persona puede estar sobrada para una carrera y lejos de otra con
exactamente los mismos puntajes.
"""

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    event,
)
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
    #: Nombre y universidad sin tildes y en minúsculas, para buscar.
    #: Nadie escribe "ENFERMERÍA" con tilde en un buscador, y un ILIKE contra
    #: el nombre original no encuentra nada. Es una columna y no `unaccent()`
    #: de Postgres para no depender de una extensión y para que la búsqueda se
    #: comporte igual en los tests.
    busqueda: Mapped[str] = mapped_column(String(400), index=True, default="")

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

    #: Requisitos oficiales de POSTULACIÓN (no son los puntajes de corte, que
    #: se publican después de cada proceso). Sin alcanzarlos la postulación ni
    #: siquiera se puede hacer, así que son la primera barrera real.
    ponderado_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    promedio_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    vacantes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    proceso: Mapped[int] = mapped_column(Integer)
    fuente: Mapped[str] = mapped_column(String(300))

    metas: Mapped[list["MetaUsuario"]] = relationship(back_populates="carrera")


class MetaUsuario(Base):
    """Una carrera dentro de la lista de postulación del estudiante.

    En Chile no se postula a una carrera: se postulan hasta diez en orden de
    preferencia, y ese orden decide dónde queda uno. Por eso hay una fila por
    carrera y no una meta única — la pregunta que importa no es "¿alcanzo para
    esta?" sino "¿hasta qué preferencia alcanzo?".

    NEM y ranking NO viven acá sino en el usuario: son datos de la persona y no
    de cada postulación, y repetirlos por fila garantizaba que algún día
    estuvieran en desacuerdo entre sí.
    """

    __tablename__ = "user_goals"
    __table_args__ = (UniqueConstraint("user_id", "carrera_id", name="uq_meta_usuario_carrera"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    carrera_id: Mapped[int] = mapped_column(ForeignKey("carreras.id"), index=True)

    #: 1 es la primera preferencia. El sistema real admite hasta 10.
    preferencia: Mapped[int] = mapped_column(Integer, default=1)

    user: Mapped["User"] = relationship(back_populates="goal")
    carrera: Mapped["Carrera"] = relationship(back_populates="metas")


def _texto_de_busqueda(carrera: Carrera) -> str:
    """Nombre, universidad y sede, sin tildes y en minúsculas."""
    from paes_api.modules.goals.service import normalizar

    return normalizar(f"{carrera.nombre} {carrera.universidad} {carrera.sede}")


@event.listens_for(Carrera, "before_insert")
@event.listens_for(Carrera, "before_update")
def _mantener_busqueda(mapper, connection, target: Carrera) -> None:
    """`busqueda` se deriva sola, siempre.

    Es un dato derivado, y dejar que cada llamador se acuerde de llenarlo es
    garantizar que algún día alguien no lo haga: esa carrera existiría en la
    base y sería invisible en el buscador, que es la peor clase de error —no
    falla, simplemente no aparece.
    """
    target.busqueda = _texto_de_busqueda(target)
