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


class EmbudoOut(BaseModel):
    """De visita anónima a ensayo terminado, en los últimos 30 días.

    Es la pregunta que ningún total responde: no importa cuánta gente entra si
    no se sabe dónde deja de avanzar. Las tasas viajan como null cuando el
    denominador es cero, porque un 0% se leería como "nadie convierte" cuando
    en realidad nadie llegó todavía a ese paso.
    """

    visitantes: int
    #: Correos dejados por gente sin cuenta (tabla `leads`). Es el paso
    #: intermedio entre mirar y registrarse: quien lo deja todavía no es un
    #: usuario, pero ya dejó de ser un visitante anónimo irrecuperable.
    correos_dejados: int
    registrados: int
    #: Cuentas creadas en la ventana que además iniciaron al menos un ensayo.
    con_ensayo: int
    con_ensayo_terminado: int
    tasa_registro: float | None
    tasa_activacion: float | None
    tasa_finalizacion: float | None
    #: Navegadores que estuvieron anónimos y después aparecieron con sesión.
    #: Es la única medida directa de conversión que permite el visitor_id.
    visitantes_convertidos: int


class RetencionOut(BaseModel):
    """Si la gente vuelve. Un registro que no vuelve es un registro perdido."""

    #: Usuarios con actividad en 1, en 2-3 y en 4 o más días distintos (30 días).
    un_dia: int
    dos_a_tres: int
    cuatro_o_mas: int
    #: De los registrados hace 7 días o más, cuántos tuvieron actividad después
    #: del día en que se registraron. `base` es cuántos podían hacerlo.
    volvieron: int
    base_volvieron: int


class UsoPrueba(BaseModel):
    subject: str
    iniciados: int
    terminados: int
    puntaje_promedio: float | None


class EnsayosOut(BaseModel):
    """Qué se rinde y qué se abandona."""

    iniciados: int
    terminados: int
    #: En curso y sin tocar hace más de un día: en la práctica, abandonados.
    abandonados: int
    tasa_finalizacion: float | None
    duracion_mediana_min: float | None
    por_prueba: list[UsoPrueba]


class CoberturaPrueba(BaseModel):
    subject: str
    #: Preguntas activas en el banco para esa prueba.
    banco: int
    #: Cuántas trae la prueba oficial del DEMRE.
    oficiales: int
    #: banco / oficiales. Bajo 1 significa que no alcanza para un ensayo completo.
    ensayos_completos: float
    #: Preguntas del banco que nunca ha respondido nadie.
    nunca_respondidas: int


class BancoOut(BaseModel):
    """Salud del contenido: si el banco alcanza para lo que la portada promete."""

    por_prueba: list[CoberturaPrueba]
    #: Nodos publicados con menos de 5 preguntas: aparecen practicables y se
    #: agotan al primer intento.
    nodos_flacos: list[str]


class VisitanteDetalle(BaseModel):
    """Una fila por navegador distinto.

    `visitor` es solo el prefijo del identificador aleatorio: alcanza para
    distinguir filas entre sí y no expone el valor completo, que es lo único
    con lo que se podría seguir a alguien entre sesiones.
    """

    visitor: str
    device: str | None
    os: str | None
    browser: str | None
    visitas: int
    #: Días distintos con actividad. Uno solo sugiere alguien de paso.
    dias: int
    primera: datetime
    ultima: datetime
    #: Si en algún momento navegó con sesión iniciada.
    con_cuenta: bool


class Canal(BaseModel):
    """Por dónde llegó la gente. `origen` None significa entrada directa."""

    origen: str | None
    visitas: int
    visitantes: int


class VisitantesOut(BaseModel):
    """Con qué equipos entra la gente.

    Existe para responder una pregunta concreta: si 27 visitantes son 27
    personas o una sola probando el sitio. La diversidad de dispositivos no lo
    prueba, pero lo delata: 27 navegadores idénticos en el mismo día no son 27
    personas.
    """

    por_dispositivo: dict[str, int]
    por_sistema: dict[str, int]
    por_navegador: dict[str, int]
    #: Visitas registradas antes de que se guardaran estas categorías.
    sin_clasificar: int
    #: Visitas de rastreadores declarados, EXCLUIDAS de todo lo demás. Se
    #: informan aparte en vez de borrarse: saber cuántos bots pasan también
    #: dice algo del sitio, y esconderlos impediría notar si la heurística
    #: está descartando gente real.
    bots: int
    #: De dónde llegaron, ya sin bots. El origen None es entrada directa:
    #: alguien que escribió la dirección o vino de un enlace sin referente.
    canales: list[Canal]
    recientes: list[VisitanteDetalle]


class ResultadoPrueba(BaseModel):
    subject: str
    ensayos: int
    mejor: int | None
    ultimo: int | None


class AlumnoDetalle(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    last_login_at: datetime | None
    #: Lo que declaró en el cuestionario de bienvenida, si lo respondió.
    curso: str | None
    pruebas_objetivo: str | None
    horas_semana: int | None
    ensayos_iniciados: int
    ensayos_terminados: int
    respuestas: int
    tasa_acierto: float | None
    mejor_puntaje: int | None
    dias_activos: int
    por_prueba: list[ResultadoPrueba]


class AlumnosOut(BaseModel):
    """Qué hizo cada cuenta registrada. Es el detalle detrás de los promedios."""

    total: int
    detalle: list[AlumnoDetalle]


class EmbudoCampanaOut(BaseModel):
    """El embudo de UNA campaña, en los últimos 30 días.

    Es la pregunta que motivó todo esto: antes de gastar el primer peso en
    publicidad hay que poder responder qué anuncio trajo a quien terminó
    pagando. El referrer no alcanza —el navegador interno de Instagram muchas
    veces no manda ninguno, y cuando manda "instagram.com" todos los anuncios
    se ven iguales—, así que la campaña viaja en la URL y se guarda en la
    visita.

    ATRIBUCIÓN DE PRIMER TOQUE: cada visitante cuenta para la PRIMERA campaña
    que lo trajo, aunque después vuelva por otra. No es la única forma de
    repartir el crédito, pero es la única que se puede sostener sin inventar
    pesos entre toques.

    `campaign` en null es el tráfico que llegó sin campaña: directo, orgánico o
    un enlace sin etiquetar. Va como una fila más para que la tabla sume el
    total real y se vea qué parte del tráfico está atribuida.
    """

    source: str | None
    medium: str | None
    campaign: str | None
    #: La creatividad concreta. Dos filas con la misma campaign y distinto
    #: content son dos anuncios de la misma campaña.
    content: str | None

    #: Navegadores distintos que entraron por esta campaña.
    visitantes: int
    #: De esos, cuántos aparecieron después con una cuenta iniciada.
    registrados: int
    #: De esos, cuántos terminaron al menos un ensayo.
    con_ensayo_terminado: int
    #: De esos, cuántos pagaron de verdad. Cuenta órdenes confirmadas, no
    #: suscripciones: un plan regalado con código no es plata que entró.
    pagaron: int

    tasa_registro: float | None
    #: Sobre visitantes, no sobre registrados: la pregunta del anuncio es
    #: cuánto cuesta traer a alguien que paga, no cuánto convierte el producto.
    tasa_pago: float | None


class AdminMetricsOut(BaseModel):
    generado_en: datetime
    usuarios: UsuariosOut
    sesiones: SesionesOut
    visitas: VisitasOut
    contenido: ContenidoOut
    embudo: EmbudoOut
    campanas: list[EmbudoCampanaOut]
    retencion: RetencionOut
    ensayos: EnsayosOut
    banco: BancoOut
    visitantes: VisitantesOut
    alumnos: AlumnosOut
