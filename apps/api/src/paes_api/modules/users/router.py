from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.core.security import create_access_token
from paes_api.modules.users import service
from paes_api.modules.users.deps import get_current_user
from paes_api.modules.users.models import User
from paes_api.modules.users.schemas import (
    LoginIn,
    RegisterIn,
    TokenOut,
    UpdateMeIn,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> TokenOut:
    user = service.register_user(db, payload)
    if user is None:
        raise HTTPException(status_code=409, detail="Ese correo ya está registrado")
    return TokenOut(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = service.authenticate(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    return TokenOut(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


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
