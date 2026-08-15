from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    created_at: datetime
    avatar_url: str | None = None
    #: Si es False, la cuenta entró con Google y aún no define contraseña.
    has_password: bool = True
    #: La web solo lo usa para mostrar u ocultar el enlace al panel. Quien
    #: manda es la API: /api/admin exige el rol en cada llamada.
    is_admin: bool = False


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=120)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginIn(BaseModel):
    """`credential` es el ID token (JWT) que entrega Google Identity Services."""

    credential: str


class AuthConfigOut(BaseModel):
    """Qué puede hacer este despliegue, para que la interfaz no prometa de más."""

    google_enabled: bool
    #: False cuando el servidor no tiene SMTP: la recuperación de contraseña
    #: no puede enviar el enlace, y la pantalla tiene que decirlo en vez de
    #: prometer un correo que nunca va a llegar.
    email_enabled: bool = False


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UpdateMeIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    current_password: str | None = None
    new_password: str | None = Field(default=None, min_length=8, max_length=128)


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
