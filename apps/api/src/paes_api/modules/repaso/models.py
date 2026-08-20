from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from paes_api.shared.base import Base


class RepasoItem(Base):
    """Una pregunta que el alumno falló y que va a volver hasta que la domine.

    Sin esto, fallar una pregunta no tenía ninguna consecuencia: el alumno leía
    la explicación, cerraba el ensayo y no la volvía a ver nunca. El banco tiene
    1.862 preguntas y se sortean al azar, así que la probabilidad de reencontrar
    justo la que no entendió es cercana a cero.

    Guarda el ESTADO del repaso, no las respuestas: cada respuesta sigue
    quedando en `practice_answers` como cualquier otra, y de ahí salen la racha
    y la analítica. Esta tabla solo dice cuándo toca la próxima vez.
    """

    __tablename__ = "repaso_items"
    __table_args__ = (
        # Una pregunta entra UNA vez a la cola de un alumno. Sin esto, dos
        # ensayos donde falló la misma pregunta la programarían dos veces y la
        # vería repetida dentro de la misma sesión.
        UniqueConstraint("user_id", "question_id", name="uq_repaso_usuario_pregunta"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)

    #: Peldaño de la escalera de intervalos. Ver `ESCALERA_DIAS` en el service.
    nivel: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    #: Cuándo vuelve a aparecer. NULL cuando ya está dominada: sin fecha no
    #: entra en ninguna consulta de pendientes, que es exactamente lo que
    #: significa haberla dominado.
    proxima_fecha: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

    #: Cuántas veces la ha respondido DENTRO del repaso.
    veces_vista: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    #: Cuántas veces la ha vuelto a fallar dentro del repaso. Es el dato que
    #: distingue "no la había leído bien" de "no entiende el tema".
    veces_fallada: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    actualizado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    @property
    def dominada(self) -> bool:
        return self.proxima_fecha is None
