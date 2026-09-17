from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from paes_api.shared.base import Base

if TYPE_CHECKING:
    from paes_api.modules.content.models import Question


class ReportePregunta(Base):
    """Un alumno avisa que una pregunta del banco está mal.

    Existe porque el banco lo escribimos nosotros y tiene miles de preguntas:
    `verificar_banco.py` recalcula la aritmética y comprueba la estructura,
    pero no puede darse cuenta de que un enunciado es ambiguo, de que dos
    alternativas son defendibles, o de que la clave quedó apuntando a la que
    no es. Eso lo ve el que está respondiendo, y hasta ahora no tenía dónde
    decirlo: el único camino era escribir un correo en medio del ensayo.

    Una fila por aviso, no un contador como en `ErrorCliente`: acá lo que
    importa es el comentario de cada persona --es el dato que permite decidir
    si la pregunta se corrige o el alumno se equivocó-- y no se puede agrupar
    sin perderlo.
    """

    __tablename__ = "reportes_pregunta"

    id: Mapped[int] = mapped_column(primary_key=True)
    #: La pregunta señalada. Si se borra del banco, el aviso se va con ella:
    #: sin la pregunta no hay nada que revisar.
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), index=True
    )
    #: Quién avisó, si tenía sesión. NULL en la demo, que se responde sin
    #: cuenta y es justamente donde entra gente que nunca nos va a escribir.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    #: Qué le pareció que estaba mal, de las categorías del formulario.
    motivo: Mapped[str] = mapped_column(String(30))
    #: Lo que escribió, si escribió algo. Opcional a propósito: pedir un texto
    #: obligatorio en el minuto 80 de un ensayo es pedir que nadie reporte.
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    #: Dónde estaba cuando reportó: "ensayo", "revision" o "practica". Un aviso
    #: dado durante el ensayo, sin ver la respuesta correcta, vale distinto que
    #: uno dado en la retroalimentación.
    contexto: Mapped[str] = mapped_column(String(20))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    #: Cuándo se revisó. NULL mientras esté pendiente; es lo que separa la
    #: bandeja de entrada del historial.
    revisado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    #: La pregunta reportada. El panel la muestra entera --enunciado, nodo y
    #: la alternativa marcada como correcta-- para poder decidir sin salir de
    #: ahí ni buscarla en `seed_data.py`.
    question: Mapped["Question"] = relationship("Question")
