from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.core.security import create_access_token
from paes_api.modules.users import service
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User
from paes_api.modules.users.schemas import (
    AuthConfigOut,
    ForgotPasswordIn,
    GoogleLoginIn,
    LoginIn,
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
    return TokenOut(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = service.authenticate(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    return TokenOut(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.get("/config", response_model=AuthConfigOut)
def auth_config() -> AuthConfigOut:
    """La web consulta esto para saber si mostrar el botón de Google."""
    return AuthConfigOut(google_enabled=bool(get_settings().google_client_id))


@router.post("/google", response_model=TokenOut)
def login_with_google(payload: GoogleLoginIn, db: Session = Depends(get_db)) -> TokenOut:
    try:
        user = service.login_with_google(
            db, payload.credential, get_settings().google_client_id
        )
    except service.GoogleAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
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
