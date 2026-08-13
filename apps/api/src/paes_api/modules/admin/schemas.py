from datetime import datetime

from pydantic import BaseModel


class ConteoPeriodo(BaseModel):
    """El mismo número medido en tres ventanas. Un solo total no dice si algo
    está creciendo o si pasó hace meses."""

    hoy: int
    ultimos_7: int
    ultimos_30: int
    total: int


class UsuarioResumen(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    last_login_at: datetime | None = None
    ensayos: int


class SerieDia(BaseModel):
    dia: str
    valor: int


class RutaVisitas(BaseModel):
    path: str
    visitas: int
    visitantes: int


class PreguntaFallada(BaseModel):
    question_id: int
    stem: str
    axis: str
    respuestas: int
    tasa_acierto: float


class NodoFlojo(BaseModel):
    code: str
    name: str
    respuestas: int
    tasa_acierto: float


class UsuariosOut(BaseModel):
    registros: ConteoPeriodo
    nuevos_por_dia: list[SerieDia]
    ultimos: list[UsuarioResumen]


class SesionesOut(BaseModel):
    entradas: ConteoPeriodo
    #: Cuentas distintas que entraron en la ventana, no número de entradas.
    activos_7: int
    activos_30: int
    por_metodo: dict[str, int]
    entradas_por_dia: list[SerieDia]


class VisitasOut(BaseModel):
    vistas: ConteoPeriodo
    visitantes: ConteoPeriodo
    #: Visitas sin sesión iniciada, que es la gente que todavía no se registra.
    anonimas_7: int
    vistas_por_dia: list[SerieDia]
    top_rutas: list[RutaVisitas]


class ContenidoOut(BaseModel):
    ensayos: ConteoPeriodo
    puntaje_promedio: float | None
    respuestas_totales: int
    tasa_acierto_global: float | None
    preguntas_mas_falladas: list[PreguntaFallada]
    nodos_mas_flojos: list[NodoFlojo]


class AdminMetricsOut(BaseModel):
    generado_en: datetime
    usuarios: UsuariosOut
    sesiones: SesionesOut
    visitas: VisitasOut
    contenido: ContenidoOut
