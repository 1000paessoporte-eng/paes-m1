"""Lectura pública del catálogo de carreras.

Solo consultas de lectura: nada de lo que hay acá escribe en la base. Es el
único módulo cuyo consumidor no tiene sesión, así que cada función asume que
la entrada viene de internet y la valida antes de tocar la base.
"""

from collections import defaultdict
from collections.abc import Callable
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from paes_api.modules.carreras.schemas import RegionConComunasOut, UniversidadOut
from paes_api.modules.goals.models import Carrera
from paes_api.modules.goals.service import buscar_carreras as _buscar

#: Las regiones de norte a sur, como las nombra el SIES. El selector las lista
#: en este orden —el del mapa—, no alfabético: quien busca "más al sur" espera
#: bajar por la lista, no saltar de la A a la Z. Una región que no esté acá
#: (nombre nuevo del SIES) igual aparece, al final y por orden alfabético.
ORDEN_REGIONES = [
    "Arica y Parinacota",
    "Tarapacá",
    "Antofagasta",
    "Atacama",
    "Coquimbo",
    "Valparaíso",
    "Metropolitana",
    "O'Higgins",
    "Maule",
    "Ñuble",
    "Biobío",
    "La Araucanía",
    "Los Ríos",
    "Los Lagos",
    "Aysén",
    "Magallanes",
]


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


def buscar(
    db: Session,
    texto: str,
    region: str | None = None,
    comuna: str | None = None,
) -> list[Carrera]:
    """Busca carreras por nombre, universidad o sede, y/o por ubicación. Sin sesión.

    Reusa la misma función que el buscador del alumno con sesión
    (`goals.service.buscar_carreras`): que el resultado dependa de si estás
    conectado sería una diferencia sin ninguna razón detrás.

    El texto llega desde internet, así que se acota antes de tocar la base: un
    `LIKE` con una cadena de 10 KB no encuentra nada pero igual viaja a
    Postgres, y una consulta de 200 palabras encadena 200 condiciones.

    Con `region` o `comuna` la búsqueda es válida aunque no haya texto —"todas
    las de la Región de Aysén" es una consulta entera—; y un texto de una o dos
    letras se ignora en vez de anular el filtro de ubicación.
    """
    texto = texto.strip()[:120]
    region = (region or "").strip()[:80] or None
    comuna = (comuna or "").strip()[:80] or None
    if len(texto) < 3 and not region and not comuna:
        # Con una o dos letras el resultado no discrimina nada: "me" está
        # dentro de medicina, comercio, ingeniería comercial y otras 300.
        return []
    # Un texto demasiado corto no debe filtrar, pero tampoco anular la búsqueda
    # cuando lo que acota es la ubicación.
    texto_util = texto if len(texto) >= 3 else ""
    return _buscar(db, texto_util, limite=LIMITE_BUSQUEDA, region=region, comuna=comuna)


def ubicaciones(db: Session) -> list[RegionConComunasOut]:
    """Las regiones y comunas donde hay carreras, para poblar el filtro.

    Solo lo que existe en el catálogo: mostrar una región sin carreras sería
    ofrecer un filtro que siempre devuelve vacío. Las comunas van agrupadas
    bajo su región porque el selector de comuna depende de la región elegida.

    Una región puede aparecer con carreras pero sin comunas: son las que se
    cruzaron con el SIES a nivel de región pero cuya comuna quedó ambigua (ver
    `scripts/asignar_geo_carreras.py`). La región se ofrece igual; su lista de
    comunas simplemente no las incluye.
    """
    filas = db.execute(
        select(Carrera.region, Carrera.comuna).where(Carrera.region.is_not(None)).distinct()
    ).all()
    comunas_por_region: dict[str, set[str]] = defaultdict(set)
    for region, comuna in filas:
        comunas_por_region[region]  # asegura la región aunque no traiga comuna
        if comuna:
            comunas_por_region[region].add(comuna)

    def orden(region: str) -> tuple[int, str]:
        indice = ORDEN_REGIONES.index(region) if region in ORDEN_REGIONES else len(ORDEN_REGIONES)
        return (indice, region)

    return [
        RegionConComunasOut(region=region, comunas=sorted(comunas_por_region[region]))
        for region in sorted(comunas_por_region, key=orden)
    ]


#: Cuántas fichas hermanas acompañan a una carrera. Suficiente para que la
#: comparación sea real —Derecho se dicta en 22 universidades, Medicina en 17—
#: y corto para que el bloque siga siendo un vistazo y no un segundo catálogo.
LIMITE_RELACIONADAS = 12

#: Cuántas filas se traen antes de agrupar por universidad.
TECHO_CANDIDATAS = 120


def relacionadas(db: Session, carrera: Carrera) -> tuple[list[Carrera], list[Carrera]]:
    """La misma carrera en otras universidades, y otras carreras de la suya.

    Existe porque la ficha de una carrera era un callejón sin salida: 296
    palabras y ningún enlace a otra. Quien llega desde Google no busca una
    carrera concreta, busca DÓNDE le alcanza, y tenía que volver al índice y
    empezar de nuevo para comparar.

    Las mismas por ponderado mínimo ascendente, con las que no lo publican al
    final: quien compara quiere ver primero dónde entra más fácil, y un `NULL`
    no es un cero -- el DEMRE no publicó ese dato para 1.153 de las 1.855.

    **Una fila por universidad, no una por sede.** Kinesiología aparece 49
    veces en el catálogo, pero la Andrés Bello ocupa tres de esas filas con
    sedes distintas: sin agrupar, media lista era la misma universidad
    repetida y la comparación no comparaba nada. Se queda la sede de menor
    ponderado, que es la que responde "dónde entro".

    La deduplicación se hace acá y no con `DISTINCT ON`, que es de Postgres:
    los tests corren sobre SQLite y el módulo no tiene por qué atarse al motor
    para algo que son doce filas.
    """
    return (
        _una_por(
            _consulta_ordenada(
                db,
                Carrera.nombre == carrera.nombre,
                orden=(Carrera.ponderado_min.asc().nullslast(), Carrera.universidad),
            ),
            clave=lambda c: c.universidad,
            excluir=carrera,
        ),
        _una_por(
            _consulta_ordenada(
                db,
                Carrera.universidad == carrera.universidad,
                orden=(Carrera.nombre,),
            ),
            clave=lambda c: c.nombre,
            excluir=carrera,
        ),
    )


def _consulta_ordenada(db: Session, filtro: Any, orden: tuple[Any, ...]) -> list[Carrera]:
    """Trae candidatas de sobra para poder agrupar sin quedarse corto.

    El límite se aplica DESPUÉS de agrupar por universidad, así que pedir solo
    doce filas dejaría la lista en cuatro cuando una universidad ocupa varias
    sedes. El techo evita traerse las 1.855 por si alguna carrera existiera en
    todas.
    """
    return list(
        db.execute(select(Carrera).where(filtro).order_by(*orden).limit(TECHO_CANDIDATAS))
        .scalars()
        .all()
    )


def _una_por(
    candidatas: list[Carrera],
    clave: Callable[[Carrera], str],
    excluir: Carrera,
) -> list[Carrera]:
    """Se queda con la primera de cada clave, respetando el orden que ya trae."""
    vistas: set[str] = set()
    salida: list[Carrera] = []
    for c in candidatas:
        if c.id == excluir.id or clave(c) in vistas:
            continue
        vistas.add(clave(c))
        salida.append(c)
        if len(salida) == LIMITE_RELACIONADAS:
            break
    return salida
