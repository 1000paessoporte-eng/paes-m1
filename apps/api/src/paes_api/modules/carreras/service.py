"""Lectura pública del catálogo de carreras.

Solo consultas de lectura: nada de lo que hay acá escribe en la base. Es el
único módulo cuyo consumidor no tiene sesión, así que cada función asume que
la entrada viene de internet y la valida antes de tocar la base.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from paes_api.modules.carreras.schemas import UniversidadOut
from paes_api.modules.goals.models import Carrera
from paes_api.modules.goals.service import buscar_carreras as _buscar


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


def universidades(db: Session) -> list[UniversidadOut]:
    """Las universidades del catálogo, con cuántas carreras tiene cada una.

    Lo agrupa Postgres, no el front: contar en Python obligaba a traerse las
    1.855 filas enteras para terminar con 47 números.
    """
    filas = db.execute(
        select(Carrera.universidad, func.count(Carrera.id))
        .group_by(Carrera.universidad)
        .order_by(func.count(Carrera.id).desc(), Carrera.universidad)
    ).all()
    return [UniversidadOut(universidad=nombre, carreras=total) for nombre, total in filas]


#: Cuántos resultados devuelve la búsqueda pública. Corto a propósito: quien
#: busca "medicina" no revisa 60 fichas, refina la búsqueda.
LIMITE_BUSQUEDA = 25


def buscar(db: Session, texto: str) -> list[Carrera]:
    """Busca carreras por nombre, universidad o sede. Sin sesión.

    Reusa la misma función que el buscador del alumno con sesión
    (`goals.service.buscar_carreras`): que el resultado dependa de si estás
    conectado sería una diferencia sin ninguna razón detrás.

    El texto llega desde internet, así que se acota antes de tocar la base: un
    `LIKE` con una cadena de 10 KB no encuentra nada pero igual viaja a
    Postgres, y una consulta de 200 palabras encadena 200 condiciones.
    """
    texto = texto.strip()[:120]
    if len(texto) < 3:
        # Con una o dos letras el resultado no discrimina nada: "me" está
        # dentro de medicina, comercio, ingeniería comercial y otras 300.
        return []
    return _buscar(db, texto, limite=LIMITE_BUSQUEDA)
