from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from paes_api.shared.base import Base

if TYPE_CHECKING:
    from paes_api.modules.billing.models import Subscription
    from paes_api.modules.exam_focus.models import ExamAttempt
    from paes_api.modules.goals.models import MetaUsuario
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

    #: El colegio al que pertenece, si entró con un código. NULL para quien usa
    #: la plataforma por su cuenta, que es el caso normal.
    #:
    #: Va en el usuario y no en una tabla aparte porque una persona pertenece a
    #: un curso a la vez: una tabla de membresías habilitaría estados que no
    #: existen --dos colegios, o ninguno con fila-- sin comprar nada.
    colegio_id: Mapped[int | None] = mapped_column(
        ForeignKey("colegios.id"), nullable=True, index=True
    )
    #: True si es profesor de ese colegio. El resto son alumnos.
    es_profesor: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    #: Última entrada exitosa. Sirve para "quién sigue activo" sin recorrer
    #: toda la tabla de eventos.
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Cuestionario de bienvenida ──────────────────────────────────────
    # Se pregunta una sola vez, al primer inicio de sesión, y sirve para que la
    # plataforma se configure sola: qué prueba abre por defecto, con qué
    # urgencia y desde qué punto de partida. Guardar respuestas que después no
    # cambian nada es hacerle perder el tiempo al estudiante.

    #: Pruebas que va a rendir, separadas por coma ("m1,lectora"). La primera
    #: es la principal: es la que abre el árbol y el configurador de ensayo.
    pruebas_objetivo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    #: "tercero", "cuarto" o "egresado".
    curso: Mapped[str | None] = mapped_column(String(20), nullable=True)
    #: Si es la primera vez que rinde la PAES.
    primera_vez: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    #: Su mejor puntaje anterior, si ya la rindió. Es el punto de partida real
    #: contra el que se mide el progreso.
    puntaje_anterior: Mapped[int | None] = mapped_column(Integer, nullable=True)
    #: Horas de estudio por semana que cree que puede dedicar.
    horas_semana: Mapped[int | None] = mapped_column(Integer, nullable=True)
    #: Cuándo lo respondió o lo saltó. Null = todavía no se le ha preguntado.
    onboarding_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    #: Recordatorios por correo para no perder la racha. Opt-in explícito: se
    #: activa al registrarse y se puede apagar en el perfil o desde el enlace
    #: que va al pie de cada correo. Nunca se manda a quien lo apagó.
    recordatorios_email: Mapped[bool] = mapped_column(Boolean, default=True)
    #: Cuándo se le mandó el último, para no escribirle todos los días.
    ultimo_recordatorio: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    #: Puntajes de NEM y ranking, tal como vienen en el informe del estudiante.
    #: Son de la persona, no de cada carrera a la que postula.
    puntaje_nem: Mapped[int | None] = mapped_column(Integer, nullable=True)
    puntaje_ranking: Mapped[int | None] = mapped_column(Integer, nullable=True)

    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    goal: Mapped[list["MetaUsuario"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    skill_progress: Mapped[list["UserSkillProgress"]] = relationship(
        back_populates="user"
    )
    exam_attempts: Mapped[list["ExamAttempt"]] = relationship(back_populates="user")

    @property
    def has_password(self) -> bool:
        """False en cuentas de Google que aún no definen una contraseña."""
        return self.hashed_password is not None

    @property
    def tiene_colegio(self) -> bool:
        """Si la cuenta pertenece a un curso.

        Existe para que /api/auth/me pueda decidir si el menú muestra
        "Mi curso" sin una consulta aparte."""
        return self.colegio_id is not None


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
