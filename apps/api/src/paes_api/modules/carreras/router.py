"""Endpoints públicos del catálogo de carreras.

Son las únicas rutas del proyecto pensadas para que las visite Google. No
piden sesión, así que llevan límite por IP como el resto de lo público
(ver modules/demo/router.py y modules/users/router.py).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.modules.carreras import service
from paes_api.modules.carreras.schemas import (
    CarreraBusquedaOut,
    CarreraCatalogoOut,
    CarreraPublicaOut,
    CarreraRelacionadaOut,
    CarreraRelacionadasOut,
    RegionConComunasOut,
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


@router.get("/buscar", response_model=list[CarreraBusquedaOut])
@limiter.limit("30/minute")
def buscar_carreras(
    request: Request,
    q: str = Query(default="", max_length=120),
    region: str = Query(default="", max_length=80),
    comuna: str = Query(default="", max_length=80),
    db: Session = Depends(get_db),
) -> list[Carrera]:
    """Busca carreras por nombre, universidad o sede, y filtra por ubicación. Público.

    Es la pregunta con la que la gente llega de verdad —cuánto puntaje
    necesita para la carrera que quiere—, y hasta ahora el buscador vivía
    detrás del login. `region` y `comuna` acotan el resultado, y sirven solas:
    se puede pedir "todas las de tal comuna" sin escribir nada. Va ANTES de
    `/{codigo}`, como el resto.
    """
    return service.buscar(db, q, region=region, comuna=comuna)


@router.get("/ubicaciones", response_model=list[RegionConComunasOut])
@limiter.limit("60/minute")
def listar_ubicaciones(
    request: Request, db: Session = Depends(get_db)
) -> list[RegionConComunasOut]:
    """Las regiones y comunas con carreras, para poblar el filtro de ubicación.

    Va ANTES de `/{codigo}`: si no, FastAPI leería "ubicaciones" como el código
    de una carrera. Las comunas viajan agrupadas bajo su región porque el
    selector de comuna depende de la región elegida.
    """
    return service.ubicaciones(db)


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


@router.get("/{codigo}/relacionadas", response_model=CarreraRelacionadasOut)
@limiter.limit("60/minute")
def ver_relacionadas(
    request: Request, codigo: str, db: Session = Depends(get_db)
) -> CarreraRelacionadasOut:
    """Por dónde seguir desde la ficha de una carrera.

    Va aparte de `/{codigo}` y no dentro: la ficha es lo que la página
    necesita para pintar, y esto es lo que necesita para no ser un callejón
    sin salida. Separadas, la página las pide en paralelo y un fallo acá no
    deja sin ponderaciones a quien vino a verlas.
    """
    carrera = service.por_codigo(db, codigo)
    if carrera is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Esa carrera no existe"
        )
    misma_carrera, misma_universidad = service.relacionadas(db, carrera)
    return CarreraRelacionadasOut(
        misma_carrera=[CarreraRelacionadaOut.model_validate(c) for c in misma_carrera],
        misma_universidad=[
            CarreraRelacionadaOut.model_validate(c) for c in misma_universidad
        ],
    )
