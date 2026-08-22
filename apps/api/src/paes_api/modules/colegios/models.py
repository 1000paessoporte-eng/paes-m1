from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from paes_api.modules.exam_focus.models import Pace
from paes_api.modules.skill_tree.models import Subject
from paes_api.shared.base import Base


class Colegio(Base):
    """Un establecimiento con su curso adentro.

    El plan Colegios se anunciaba en la página de planes con precio y con
    cuatro promesas --cuentas para el curso, panel del profesor, informes por
    estudiante y ensayos programados-- y ninguna existía. Esto es lo que hace
    verdaderas esas promesas.

    El profesor NO crea cuentas por el alumno: le entrega un código y cada uno
    entra con la suya. Crear cuentas ajenas significaría manejar contraseñas de
    menores de edad, y además el alumno que se cambia de colegio perdería su
    historial. Su cuenta es suya; el colegio es una pertenencia, no un dueño.
    """

    __tablename__ = "colegios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(160))
    #: El código que el profesor le dicta al curso. Corto y sin caracteres que
    #: se confundan al leerlos en voz alta o copiarlos de una pizarra.
    codigo: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    #: Quién lo creó, o NULL si esa persona borró su cuenta.
    #:
    #: Admite NULL a propósito: la política de privacidad promete borrar la
    #: cuenta cuando se pide, y si esta columna fuera obligatoria borrar al
    #: profesor obligaría a borrar el curso con sus treinta alumnos adentro.
    #: El curso sobrevive; quien lo administra son los `es_profesor` que
    #: queden.
    creado_por: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    #: Hasta cuándo el curso tiene el plan pagado. NULL es un curso sin pagar,
    #: que igual funciona: el profesor ve su panel y los alumnos siguen con el
    #: plan Gratis. Lo que compra el colegio es que sus alumnos tengan Pro.
    #:
    #: Vive en el colegio y no en una suscripción por alumno a propósito: el
    #: colegio paga una vez por el año escolar, y los alumnos entran y salen
    #: del curso durante ese año. Atarlo a la cuenta obligaría a crear y
    #: cancelar treinta suscripciones a mano cada marzo.
    plan_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)


class EnsayoProgramado(Base):
    """Un ensayo que el profesor deja agendado para su curso.

    No bloquea ni obliga: aparece en el panel del alumno como algo que hay que
    rendir para una fecha, y el profesor ve quién lo hizo. Un ensayo que se
    cierra a una hora exacta necesitaría manejar zonas horarias, cortes de luz
    y reclamos, y para un curso de treinta personas la lista de quién cumplió
    resuelve el mismo problema sin nada de eso.
    """

    __tablename__ = "ensayos_programados"

    id: Mapped[int] = mapped_column(primary_key=True)
    colegio_id: Mapped[int] = mapped_column(ForeignKey("colegios.id"), index=True)
    titulo: Mapped[str] = mapped_column(String(160))
    subject: Mapped[Subject] = mapped_column(Enum(Subject))
    pace: Mapped[Pace] = mapped_column(Enum(Pace), default=Pace.OFICIAL)
    question_count: Mapped[int] = mapped_column(Integer, default=65)
    #: Para cuándo. Fecha y no instante: el profesor dice "para el viernes",
    #: no "para el viernes a las 14:32 UTC".
    fecha: Mapped[date] = mapped_column(Date, index=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
