from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from paes_api.shared.base import Base


class Lead(Base):
    """Un correo dejado por alguien que todavía NO tiene cuenta.

    Existe por un agujero concreto del embudo: quien entra a la demo, responde
    las cinco preguntas y no se registra se va sin dejar rastro, y no hay forma
    de volver a hablarle. Registrarse son varios pasos; dejar el correo, uno.

    Es lo mínimo que sirve: correo y de qué pantalla salió. Nada de IP ni de
    nombre — para escribirle a alguien basta su correo, y el dato que no se
    guarda no se puede filtrar (mismo criterio que `PageView`).

    No sustituye a `User`: cuando la persona se registra, su cuenta vive en
    `users` y esta fila queda como el registro de por dónde entró.
    """

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    #: Único: dejar el correo dos veces no crea dos filas ni es un error para
    #: quien lo deja. Se guarda normalizado en minúsculas.
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    #: Pantalla desde la que se dejó ("demo", "portada"). Sin esto no se puede
    #: saber qué parte del sitio convierte.
    source: Mapped[str] = mapped_column(String(40), default="demo")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
