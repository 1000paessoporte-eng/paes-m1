"""Lo que ve un visitante sin cuenta.

Deliberadamente NO reusa `CarreraOut` de goals: ese schema sirve al buscador
del alumno autenticado y puede crecer con campos de su meta personal. Este
viaja a páginas indexables por Google, así que su superficie tiene que poder
revisarse sola.
"""

from pydantic import BaseModel, ConfigDict


class CarreraPublicaOut(BaseModel):
    """Ficha completa de una carrera para su página pública."""

    model_config = ConfigDict(from_attributes=True)

    codigo: str
    universidad: str
    nombre: str
    sede: str

    #: Dónde se dicta, para ubicar la carrera en el mapa del país. `None`
    #: cuando el cruce con el SIES no la identificó (ver el modelo `Carrera`).
    region: str | None = None
    comuna: str | None = None

    #: Ponderaciones en porcentaje. Suman 100 entre todas.
    nem: float | None = None
    ranking: float | None = None
    lectora: float | None = None
    m1: float | None = None
    historia: float | None = None
    ciencias: float | None = None
    m2: float | None = None
    prueba_especial: float | None = None
    electivo_alternativo: bool

    #: Requisitos oficiales de POSTULACIÓN. No son puntajes de corte: el corte
    #: se publica recién al cerrar cada proceso y no lo tenemos. La página
    #: tiene que decirlo con esas palabras para no prometer lo que no sabe.
    ponderado_min: float | None = None
    promedio_min: float | None = None
    vacantes: int | None = None

    proceso: int
    fuente: str


class CarreraCatalogoOut(BaseModel):
    """Lo mínimo para armar el sitemap y el índice navegable.

    Sin ponderaciones a propósito: son 1.855 filas y el índice solo necesita
    nombrarlas y enlazarlas. La ficha completa se pide por carrera.
    """

    model_config = ConfigDict(from_attributes=True)

    codigo: str
    universidad: str
    nombre: str
    sede: str


class CarreraBusquedaOut(BaseModel):
    """Una fila de resultados del buscador.

    Es el `CarreraCatalogoOut` más la ubicación: el catálogo entero (1.855
    filas para el sitemap) no la carga para no engordar un payload que solo
    nombra y enlaza, pero un resultado de búsqueda sí la muestra —dónde queda
    la carrera es justo lo que el filtro por región y comuna deja ver.
    """

    model_config = ConfigDict(from_attributes=True)

    codigo: str
    universidad: str
    nombre: str
    sede: str
    region: str | None = None
    comuna: str | None = None


class RegionConComunasOut(BaseModel):
    """Una región y las comunas donde hay carreras, para armar el filtro.

    El selector de comuna depende de la región elegida, así que las comunas
    viajan agrupadas bajo su región y no como una lista plana: mostrar las 346
    comunas del país cuando en una región hay tres sería ruido, no ayuda.
    """

    region: str
    comunas: list[str]


class UniversidadOut(BaseModel):
    """Una universidad y cuántas carreras suyas hay en el catálogo.

    Existe para no bajar las 1.855 filas cuando lo único que se necesita son
    las 47 universidades: la portada y el índice las listan, y traerse el
    catálogo entero para contarlas es mover un megabyte para escribir un
    número.
    """

    universidad: str
    carreras: int


class CarreraRelacionadaOut(BaseModel):
    """Una ficha hermana, con lo justo para compararla de un vistazo.

    Sin las ponderaciones: el bloque de relacionadas responde "¿dónde más se
    dicta y dónde entro?", no "¿cómo se pondera allá?". Para eso se abre la
    ficha, que es exactamente lo que queremos que pase.
    """

    model_config = ConfigDict(from_attributes=True)

    codigo: str
    universidad: str
    nombre: str
    sede: str
    #: `None` en 1.153 de las 1.855: el DEMRE no publica un mínimo para todas.
    #: Va igual, y la pantalla decide cómo mostrar la ausencia.
    ponderado_min: float | None = None
    vacantes: int | None = None


class CarreraRelacionadasOut(BaseModel):
    """Los dos caminos que se le abren a quien está mirando una ficha."""

    #: La misma carrera en otras universidades, de menor a mayor ponderado
    #: mínimo. Es la comparación que trae a la gente desde Google.
    misma_carrera: list[CarreraRelacionadaOut]
    #: Otras carreras de la misma universidad, alfabéticas.
    misma_universidad: list[CarreraRelacionadaOut]
