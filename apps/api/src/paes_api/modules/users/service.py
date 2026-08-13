import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.core.email import send_email
from paes_api.core.security import hash_password, verify_password
from paes_api.modules.users.models import PasswordResetToken, User
from paes_api.modules.users.schemas import RegisterIn, UpdateMeIn

RESET_TOKEN_TTL_MINUTES = 30


def _as_aware_utc(dt: datetime) -> datetime:
    """Algunos backends (SQLite, usado en tests) devuelven datetimes naive
    incluso en columnas DateTime(timezone=True) tras el roundtrip a la DB.
    Sin esto, comparar contra datetime.now(UTC) revienta con TypeError."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


class WrongPasswordError(Exception):
    pass


class GoogleAuthError(Exception):
    """El ID token de Google no es válido, expiró o no es de esta app."""


def get_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def register_user(db: Session, payload: RegisterIn) -> User | None:
    """Retorna None si el email ya está en uso."""
    if get_by_email(db, payload.email) is not None:
        return None
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        name=payload.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_by_email(db, email)
    # Las cuentas creadas con Google no tienen contraseña: no se puede entrar
    # por este camino hasta que definan una desde su perfil.
    if user is None or user.hashed_password is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def login_with_google(db: Session, credential: str, client_id: str) -> User:
    """Valida el ID token que emitió Google y devuelve el usuario asociado.

    La verificación comprueba la firma de Google, la expiración y que el token
    haya sido emitido para ESTE client_id — sin lo último, un token válido de
    otra aplicación serviría para entrar aquí.
    """
    if not client_id:
        raise GoogleAuthError("El inicio de sesión con Google no está configurado")

    try:
        claims = google_id_token.verify_oauth2_token(
            credential, google_requests.Request(), client_id
        )
    except ValueError as exc:
        raise GoogleAuthError(str(exc)) from exc

    if not claims.get("email_verified", False):
        raise GoogleAuthError("La cuenta de Google no tiene el correo verificado")

    sub = claims["sub"]
    email = claims["email"]
    name = claims.get("name") or email.split("@")[0]
    picture = claims.get("picture")

    user = db.execute(select(User).where(User.google_sub == sub)).scalar_one_or_none()
    if user is None:
        # Mismo correo registrado antes con contraseña: se enlaza la cuenta en
        # lugar de crear una duplicada, así conserva su historial de ensayos.
        user = get_by_email(db, email)
        if user is not None:
            user.google_sub = sub
        else:
            user = User(email=email, name=name, google_sub=sub, hashed_password=None)
            db.add(user)

    user.avatar_url = picture
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, payload: UpdateMeIn) -> User:
    """Lanza WrongPasswordError si se pide cambiar la contraseña sin
    entregar (o con) la contraseña actual correcta."""
    if payload.new_password is not None:
        # Quien entró con Google todavía no tiene contraseña: puede definir una
        # sin dar la anterior, ya que su identidad ya está probada por el JWT.
        if user.hashed_password is not None and (
            payload.current_password is None
            or not verify_password(payload.current_password, user.hashed_password)
        ):
            raise WrongPasswordError
        user.hashed_password = hash_password(payload.new_password)

    if payload.name is not None:
        user.name = payload.name

    db.commit()
    db.refresh(user)
    return user


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def request_password_reset(db: Session, email: str) -> None:
    """No indica si el correo existe: el llamador siempre responde 204,
    exista o no la cuenta, para no filtrar qué correos están registrados."""
    user = get_by_email(db, email)
    if user is None:
        return

    # Cualquier token pendiente anterior queda inválido: solo el link más
    # reciente que se mandó al usuario debe funcionar.
    db.execute(
        delete(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
    )

    raw_token = secrets.token_urlsafe(32)
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            expires_at=datetime.now(UTC) + timedelta(minutes=RESET_TOKEN_TTL_MINUTES),
        )
    )
    db.commit()

    reset_url = f"{get_settings().frontend_url}/restablecer-contrasena?token={raw_token}"
    send_email(
        to=user.email,
        subject="Recupera tu contraseña en milpaes",
        body=(
            f"Hola {user.name},\n\n"
            "Recibimos una solicitud para restablecer tu contraseña en milpaes.\n"
            f"Este link es válido por {RESET_TOKEN_TTL_MINUTES} minutos y solo se puede usar una vez:\n\n"
            f"{reset_url}\n\n"
            "Si no fuiste tú, ignora este correo: tu contraseña actual sigue funcionando."
        ),
    )


def reset_password(db: Session, raw_token: str, new_password: str) -> bool:
    """Retorna False si el token no existe, ya se usó o expiró."""
    token = db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == _hash_token(raw_token)
        )
    ).scalar_one_or_none()

    if (
        token is None
        or token.used_at is not None
        or _as_aware_utc(token.expires_at) < datetime.now(UTC)
    ):
        return False

    user = db.get(User, token.user_id)
    if user is None:
        return False

    user.hashed_password = hash_password(new_password)
    token.used_at = datetime.now(UTC)
    # Invalida cualquier otro link de reset pendiente para esta cuenta.
    db.execute(
        delete(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.id != token.id,
            PasswordResetToken.used_at.is_(None),
        )
    )
    db.commit()
    return True
