from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.core.security import decode_access_token
from paes_api.modules.users.models import User

_bearer = HTTPBearer(auto_error=False)

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise _CREDENTIALS_ERROR
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise _CREDENTIALS_ERROR
    user = db.get(User, user_id)
    if user is None:
        raise _CREDENTIALS_ERROR
    return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    """Igual que `get_current_user` pero sin exigir sesión: devuelve None en vez
    de 401. Lo usan los endpoints públicos que igual quieren saber quién es
    quien llama (ej. registrar una visita como anónima o identificada)."""
    if credentials is None:
        return None
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        return None
    return db.get(User, user_id)


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """Puerta del panel de administración.

    Responde 404 y no 403 a propósito: para una cuenta normal, /api/admin no
    debe siquiera revelar que existe."""
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No encontrado")
    return user
