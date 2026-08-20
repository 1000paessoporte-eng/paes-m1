from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.modules.leads.models import Lead
from paes_api.modules.leads.schemas import LeadIn, LeadOut

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadOut, status_code=201)
@limiter.limit("5/minute")
def crear_lead(request: Request, payload: LeadIn, db: Session = Depends(get_db)) -> LeadOut:
    """Guarda un correo de alguien sin cuenta.

    Público y sin auth (esa es la gracia: se deja antes de registrarse), así
    que va con límite por IP. Repetir el mismo correo no es un error: la
    respuesta es idéntica y no se crea una fila nueva.
    """
    email = payload.email.strip().lower()
    existente = db.execute(select(Lead).where(Lead.email == email)).scalar_one_or_none()
    if existente is not None:
        return LeadOut()

    db.add(Lead(email=email, source=payload.source.value))
    try:
        db.commit()
    except IntegrityError:
        # Dos envíos del mismo correo a la vez: ambos leen "no existe" y ambos
        # insertan. El índice único evita la fila duplicada, pero sin atrapar
        # el error el segundo se iría en 500 por algo que para quien lo mandó
        # salió bien. El de la carrera perdedora ve la misma respuesta.
        db.rollback()
    return LeadOut()
