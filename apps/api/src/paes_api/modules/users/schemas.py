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
    """Qué métodos de inicio de sesión están habilitados en este despliegue."""

    google_enabled: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UpdateMeIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    current_password: str | None = None
    new_password: str | None = Field(default=None, min_length=8, max_length=128)
