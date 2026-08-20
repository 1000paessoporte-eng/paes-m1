"""Endpoints públicos del catálogo de carreras.

Son las únicas rutas del proyecto pensadas para que las visite Google. No
piden sesión, así que llevan límite por IP como el resto de lo público
(ver modules/demo/router.py y modules/users/router.py).
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.modules.carreras import service
from paes_api.modules.carreras.schemas import (
    CarreraCatalogoOut,
    CarreraPublicaOut,
    UniversidadOut,
)
from paes_api.modules.goals.models import Carrera

router = APIRouter(prefix="/carreras", tags=["carreras"])


@router.get("/catalogo", response_model=list[CarreraCatalogoOut])
@limiter.limit("30/minute")
def listar_catalogo(request: Request, db: Session = Depends(get_db)) -> list[Carrera]:
    """El catálogo entero, para el sitemap y el índice navegable.

    Límite generoso pero presente: la respuesta es de ~1.855 filas y el
    consumidor legítimo (el build del front) la pide una vez cada tanto, no
    treinta veces por minuto.
    """
    return service.catalogo(db)


@router.get("/universidades", response_model=list[UniversidadOut])
@limiter.limit("60/minute")
def listar_universidades(request: Request, db: Session = Depends(get_db)) -> list[UniversidadOut]:
    """Las 47 universidades con su número de carreras.

    Va ANTES de `/{codigo}`: si no, FastAPI intentaría leer
    "universidades" como el código de una carrera.
    """
    return service.universidades(db)


@router.get("/{codigo}", response_model=CarreraPublicaOut)
@limiter.limit("60/minute")
def ver_carrera(request: Request, codigo: str, db: Session = Depends(get_db)) -> Carrera:
    """La ficha pública de una carrera.

    404 explícito cuando el código no existe: la página de carrera se genera
    bajo demanda, y un código inventado en la URL tiene que dar "no existe" y
    no un 500.
    """
    carrera = service.por_codigo(db, codigo)
    if carrera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Esa carrera no existe"
        )
    return carrera
