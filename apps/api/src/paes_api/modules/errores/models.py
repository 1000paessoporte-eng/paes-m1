from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from paes_api.shared.base import Base


class ErrorCliente(Base):
    """Un error que reventó en el navegador de un alumno.

    Existe porque no había NINGÚN monitoreo. Si a alguien se le cae el ensayo
    en el minuto 90, hoy nadie se entera: el error ocurre en su teléfono y
    muere ahí. Con siete usuarios da lo mismo; con setecientos es la diferencia
    entre arreglarlo en una hora o en una semana.

    No se usa un proveedor externo a propósito: exigiría una cuenta más, una
    clave más y mandar datos de estudiantes a un tercero. Esto guarda lo mínimo
    para reproducir --qué falló, dónde y en qué navegador-- y se mira en el
    panel de administración que ya existe.
    """

    __tablename__ = "errores_cliente"

    id: Mapped[int] = mapped_column(primary_key=True)
    #: Quién lo sufrió, si tenía sesión. NULL en las páginas públicas.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    #: Mensaje del error, recortado. Nunca el objeto completo.
    mensaje: Mapped[str] = mapped_column(String(500))
    #: La ruta interna donde ocurrió. Sin query string: puede traer el token
    #: de restablecer contraseña.
    ruta: Mapped[str] = mapped_column(String(255), index=True)
    #: La pila, recortada. Es lo que permite ubicar la línea.
    pila: Mapped[str | None] = mapped_column(Text, nullable=True)
    #: Navegador y sistema, en las tres categorías gruesas que ya usa métricas.
    navegador: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ocurrido_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    #: Cuántas veces se repitió exactamente el mismo error en la misma ruta.
    #: Sin esto, un error en bucle llena la tabla con miles de filas iguales.
    veces: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
