"""Lectura pública del catálogo de carreras.

Solo consultas de lectura: nada de lo que hay acá escribe en la base. Es el
único módulo cuyo consumidor no tiene sesión, así que cada función asume que
la entrada viene de internet y la valida antes de tocar la base.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.goals.models import Carrera


def catalogo(db: Session) -> list[Carrera]:
    """Todas las carreras, ordenadas para que el índice sea estable.

    Se devuelven completas y sin paginar: son 1.855 filas de cuatro columnas
    cortas, y tanto el sitemap como el índice necesitan la lista entera. Paginar
    obligaría al front a encadenar peticiones para construir un sitemap, que es
    justo lo que no se quiere en cada build.
    """
    return list(
        db.execute(select(Carrera).order_by(Carrera.universidad, Carrera.nombre, Carrera.sede))
        .scalars()
        .all()
    )


def por_codigo(db: Session, codigo: str) -> Carrera | None:
    """La ficha de una carrera, o None si el código no existe.

    Devuelve None en vez de lanzar: quien llama decide el 404. El código llega
    desde la URL, así que se acota de largo antes de consultar -- un `LIKE` con
    una cadena de 10 KB no encuentra nada pero igual viaja a Postgres.
    """
    codigo = codigo.strip()
    if not codigo or len(codigo) > 10:
        return None
    return db.execute(select(Carrera).where(Carrera.codigo == codigo)).scalars().first()
