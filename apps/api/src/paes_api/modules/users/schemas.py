from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserOut(BaseModel):
    recordatorios_email: bool = True
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
    #: Si la cuenta pertenece a un curso. Solo sirve para decidir si el menú
    #: muestra "Mi curso": enlazarlo para todo el mundo pondría en la barra una
    #: sección que casi nadie tiene.
    tiene_colegio: bool = False


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


class OnboardingIn(BaseModel):
    """Respuestas del cuestionario de bienvenida. Todo es opcional: se puede
    saltar, y saltarlo también cuenta como responder —no se vuelve a preguntar."""

    pruebas_objetivo: list[str] = Field(default_factory=list, max_length=5)
    curso: str | None = Field(default=None, max_length=20)
    primera_vez: bool | None = None
    puntaje_anterior: int | None = Field(default=None, ge=100, le=1000)
    horas_semana: int | None = Field(default=None, ge=0, le=60)


class OnboardingOut(BaseModel):
    """Lo respondido, para el perfil y para configurar la plataforma."""

    model_config = ConfigDict(from_attributes=True)

    pruebas_objetivo: list[str] = []
    curso: str | None = None
    primera_vez: bool | None = None
    puntaje_anterior: int | None = None
    horas_semana: int | None = None
    #: False mientras no se le haya preguntado: es lo que dispara el
    #: cuestionario al entrar.
    respondido: bool = False


class UpdateMeIn(BaseModel):
    recordatorios_email: bool | None = None
    name: str | None = Field(default=None, min_length=1, max_length=120)
    current_password: str | None = None
    new_password: str | None = Field(default=None, min_length=8, max_length=128)


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class EliminarCuentaIn(BaseModel):
    """Confirmación para borrar la cuenta.

    La contraseña va aunque haya sesión iniciada: borrar es irreversible y no
    puede depender solo de que alguien dejó su sesión abierta. Las cuentas de
    Google no tienen contraseña, así que ahí llega en None y se omite.
    """

    password: str | None = None
