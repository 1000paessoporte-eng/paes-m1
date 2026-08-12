"""Usuario demo temporal: aún no hay autenticación implementada, así que
todos los intentos de examen se asocian a un único usuario placeholder.
Reemplazar por el usuario real de la sesión cuando exista auth."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.users.models import User

DEMO_EMAIL = "demo@paes-m1.local"


def get_or_create_demo_user(db: Session) -> User:
    user = db.execute(select(User).where(User.email == DEMO_EMAIL)).scalar_one_or_none()
    if user is not None:
        return user
    user = User(email=DEMO_EMAIL, hashed_password="", name="Estudiante Demo")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
