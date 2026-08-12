from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
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
