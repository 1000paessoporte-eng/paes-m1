"""Hashing de contraseñas (bcrypt) y JWT de sesión (HS256).

MVP consciente: el token se guarda del lado del cliente en una cookie NO
httpOnly (ver apps/web/lib/auth.ts) para poder adjuntarlo como
Authorization Bearer tanto desde Server Components como desde el navegador
(exam-runner hace fetch directo a la API). No es el diseño más hardened
posible, pero evita la complejidad de cookies cross-site entre el dominio
del front y el de la API (que además pueden ser túneles cloudflared
distintos)."""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from paes_api.core.config import get_settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14  # 14 días


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    if not hashed:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        return int(sub)
    except ValueError:
        return None
