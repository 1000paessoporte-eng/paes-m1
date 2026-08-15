from pydantic import BaseModel, ConfigDict, Field


class CarreraOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    universidad: str
    nombre: str
    sede: str
    nem: float | None = None
    ranking: float | None = None
    lectora: float | None = None
    m1: float | None = None
    historia: float | None = None
    ciencias: float | None = None
    m2: float | None = None
    prueba_especial: float | None = None
    electivo_alternativo: bool
    proceso: int
    fuente: str


class MetaIn(BaseModel):
    carrera_id: int
    #: Puntajes de 100 a 1000, tal como vienen en el informe del estudiante.
    puntaje_nem: int | None = Field(default=None, ge=100, le=1000)
    puntaje_ranking: int | None = Field(default=None, ge=100, le=1000)


class AporteOut(BaseModel):
    """Cuánto pone cada factor en el puntaje ponderado, y cuánto podría poner."""

    factor: str
    etiqueta: str
    ponderacion: float
    puntaje: int | None
    #: Puntos de ponderado que aporta hoy este factor.
    aporte: float
    #: Cuánto sube el ponderado por cada 10 puntos de mejora en este factor.
    por_cada_10: float
    #: De dónde salió el puntaje: "ensayo", "ingresado" o "falta".
    origen: str


class MetaOut(BaseModel):
    carrera: CarreraOut
    #: None si falta algún puntaje que la carrera pondera.
    ponderado: float | None
    #: Mínimo oficial para postular, si la carrera lo exige.
    aportes: list[AporteOut]
    faltantes: list[str]
    #: El factor donde una mejora rinde más: mayor ponderación y más margen.
    mejor_palanca: str | None
