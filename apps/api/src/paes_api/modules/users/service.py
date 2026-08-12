from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.security import hash_password, verify_password
from paes_api.modules.users.models import User
from paes_api.modules.users.schemas import RegisterIn, UpdateMeIn


class WrongPasswordError(Exception):
    pass


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
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(db: Session, user: User, payload: UpdateMeIn) -> User:
    """Lanza WrongPasswordError si se pide cambiar la contraseña sin
    entregar (o con) la contraseña actual correcta."""
    if payload.new_password is not None:
        if payload.current_password is None or not verify_password(
            payload.current_password, user.hashed_password
        ):
            raise WrongPasswordError
        user.hashed_password = hash_password(payload.new_password)

    if payload.name is not None:
        user.name = payload.name

    db.commit()
    db.refresh(user)
    return user
