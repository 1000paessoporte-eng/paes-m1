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
    ponderado_min: float | None = None
    promedio_min: float | None = None
    vacantes: int | None = None
    proceso: int
    fuente: str


class NotasIn(BaseModel):
    puntaje_nem: int | None = Field(default=None, ge=100, le=1000)
    puntaje_ranking: int | None = Field(default=None, ge=100, le=1000)


class PostularIn(BaseModel):
    carrera_id: int


class OrdenIn(BaseModel):
    """Los ids de carrera en el orden de preferencia deseado."""

    carrera_ids: list[int]


class AporteOut(BaseModel):
    factor: str
    etiqueta: str
    ponderacion: float
    puntaje: int | None
    aporte: float
    por_cada_10: float
    origen: str


class PostulacionOut(BaseModel):
    preferencia: int
    carrera: CarreraOut
    ponderado: float | None
    #: Puntos que faltan para el mínimo oficial de postulación. Negativo o cero
    #: significa que ya se alcanza.
    brecha: float | None
    alcanza: bool | None
    aportes: list[AporteOut]
    faltantes: list[str]
    mejor_palanca: str | None


class ProyeccionOut(BaseModel):
    """Ritmo de mejora medido sobre los ensayos ya rendidos."""

    puntos_por_mes: float | None
    ensayos_considerados: int
    dias_para_paes: int | None
    #: Puntaje proyectado a la fecha de la PAES, si hay tendencia suficiente.
    proyectado: float | None


class NodoDebilOut(BaseModel):
    code: str
    name: str
    axis: str
    accuracy: float
    attempts: int
    has_lesson: bool


class PlanSemanalOut(BaseModel):
    """El plan dimensionado con las horas que el estudiante declaró tener.

    Existe porque un plan que no cabe en la semana de alguien no es un plan, es
    una lista de deseos: el estudiante lo mira, ve que no le alcanza, y no hace
    ninguna de las cosas.
    """

    horas_semana: int | None
    #: Cuántos temas del plan alcanza a estudiar con ese tiempo.
    temas_que_caben: int
    #: Si además le da el tiempo para un ensayo corto.
    alcanza_un_ensayo: bool
    #: Minutos que suma el plan propuesto.
    minutos_estimados: int


class MetaOut(BaseModel):
    postulaciones: list[PostulacionOut]
    puntaje_nem: int | None
    puntaje_ranking: int | None
    proyeccion: ProyeccionOut
    #: Los nodos donde conviene practicar para mover la palanca de la primera
    #: preferencia que todavía no se alcanza.
    plan: list[NodoDebilOut]
    plan_para: str | None
    plan_semanal: PlanSemanalOut
