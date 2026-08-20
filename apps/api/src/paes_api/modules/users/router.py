from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from paes_api.core import email
from paes_api.core.config import get_settings
from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.core.security import create_access_token
from paes_api.modules.users import service
from paes_api.modules.users.deps import get_current_admin, get_current_user
from paes_api.modules.users.models import User
from paes_api.modules.users.schemas import (
    AuthConfigOut,
    EliminarCuentaIn,
    ForgotPasswordIn,
    GoogleLoginIn,
    LoginIn,
    OnboardingIn,
    OnboardingOut,
    RegisterIn,
    ResetPasswordIn,
    TokenOut,
    UpdateMeIn,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: RegisterIn, db: Session = Depends(get_db)) -> TokenOut:
    user = service.register_user(db, payload)
    if user is None:
        raise HTTPException(status_code=409, detail="Ese correo ya está registrado")
    # Registrarse deja la sesión abierta, así que cuenta como entrada.
    service.record_login(db, user, "password")
    return TokenOut(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = service.authenticate(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    service.record_login(db, user, "password")
    return TokenOut(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.get("/onboarding", response_model=OnboardingOut)
def ver_onboarding(user: User = Depends(get_current_user)) -> OnboardingOut:
    return OnboardingOut(**service.onboarding_de(user))


@router.put("/onboarding", response_model=OnboardingOut)
def responder_onboarding(
    payload: OnboardingIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OnboardingOut:
    service.guardar_onboarding(db, user, payload)
    return OnboardingOut(**service.onboarding_de(user))


@router.get("/config", response_model=AuthConfigOut)
def auth_config() -> AuthConfigOut:
    """Qué puede hacer este servidor, para que la interfaz no prometa de más.

    Sin SMTP configurado, "te llegará un correo con las instrucciones" es una
    promesa incumplible: el enlace de recuperación se genera igual pero queda
    en el log, y el estudiante espera algo que nunca llega. La pantalla
    necesita saberlo para decir la verdad.
    """
    ajustes = get_settings()
    return AuthConfigOut(
        google_enabled=bool(ajustes.google_client_id),
        email_enabled=bool(ajustes.smtp_host),
    )


@router.post("/google", response_model=TokenOut)
def login_with_google(payload: GoogleLoginIn, db: Session = Depends(get_db)) -> TokenOut:
    try:
        user = service.login_with_google(
            db, payload.credential, get_settings().google_client_id
        )
    except service.GoogleAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    service.record_login(db, user, "google")
    return TokenOut(
        access_token=create_access_token(user.id), user=UserOut.model_validate(user)
    )


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("3/minute")
def forgot_password(request: Request, payload: ForgotPasswordIn, db: Session = Depends(get_db)) -> None:
    """Siempre responde 204, exista o no el correo: no revela qué cuentas
    están registradas."""
    service.request_password_reset(db, payload.email)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def reset_password(request: Request, payload: ResetPasswordIn, db: Session = Depends(get_db)) -> None:
    ok = service.reset_password(db, payload.token, payload.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="El enlace no es válido o ya expiró")


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UpdateMeIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> UserOut:
    try:
        updated = service.update_user(db, user, payload)
    except service.WrongPasswordError as exc:
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta") from exc
    return UserOut.model_validate(updated)


@router.get("/diagnostico-correo")
def diagnostico_correo(user: User = Depends(get_current_admin)) -> dict[str, object]:
    """Si el correo saldría o no, y por qué.

    Existe porque "olvidé mi contraseña" responde 204 exista o no la cuenta:
    ese silencio protege la privacidad, pero también esconde una configuración
    rota. Sin esto, la única forma de enterarse de que el correo no sale es que
    alguien se quede fuera de su cuenta y lo reporte.

    Solo admin, y nunca devuelve la contraseña del SMTP: solo si está puesta.
    """
    return email.diagnostico()


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mi_cuenta(
    payload: EliminarCuentaIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    """Borra la cuenta y todo lo que cuelga de ella.

    Estaba solo en la política de privacidad como "escríbenos a hola@": pedirle
    a alguien que mande un correo para ejercer un derecho sobre sus datos es
    ponerle un trámite a lo que debería ser un botón, y este producto guarda
    datos de estudio de menores de edad.

    Pide la contraseña actual, salvo en las cuentas de Google, que no tienen.
    Borrar es irreversible y no puede depender solo de una sesión abierta en un
    computador prestado.
    """
    if not service.eliminar_cuenta(db, user, payload.password):
        raise HTTPException(status_code=401, detail="La contraseña no es correcta")
