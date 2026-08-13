from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from paes_api.shared.base import Base

if TYPE_CHECKING:
    from paes_api.modules.exam_focus.models import ExamAttempt
    from paes_api.modules.skill_tree.models import UserSkillProgress


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    #: NULL para las cuentas creadas con Google, que nunca tienen contraseña.
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    #: `sub` de Google: identificador estable de la cuenta, no cambia si la
    #: persona cambia su correo. Se usa para enlazar el mismo usuario.
    google_sub: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True, nullable=True
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    name: Mapped[str] = mapped_column(String(120))
    #: Acceso al panel de administración (/admin). Se otorga a mano con
    #: `scripts/make_admin.py`: no hay forma de volverse admin desde la web,
    #: porque el panel expone datos de todas las cuentas.
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    #: Última entrada exitosa. Sirve para "quién sigue activo" sin recorrer
    #: toda la tabla de eventos.
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    skill_progress: Mapped[list["UserSkillProgress"]] = relationship(
        back_populates="user"
    )
    exam_attempts: Mapped[list["ExamAttempt"]] = relationship(back_populates="user")

    @property
    def has_password(self) -> bool:
        """False en cuentas de Google que aún no definen una contraseña."""
        return self.hashed_password is not None


class LoginEvent(Base):
    """Una fila por entrada exitosa (contraseña o Google).

    `User.last_login_at` solo guarda la última: para responder "cuánta gente
    entró esta semana" hace falta el historial, no el estado actual."""

    __tablename__ = "login_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    #: "password" | "google". Sirve para saber cuánto se usa cada vía de entrada.
    method: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class PasswordResetToken(Base):
    """Token de un solo uso para el flujo de 'olvidé mi contraseña'.

    Se guarda el hash SHA-256 del token, no el token en sí: una fuga de la
    tabla no debe permitir a nadie resetear contraseñas ajenas. El token
    plano solo existe en el correo enviado al usuario."""

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
