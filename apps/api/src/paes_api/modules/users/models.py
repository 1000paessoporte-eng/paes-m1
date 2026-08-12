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
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    skill_progress: Mapped[list["UserSkillProgress"]] = relationship(
        back_populates="user"
    )
    exam_attempts: Mapped[list["ExamAttempt"]] = relationship(back_populates="user")
