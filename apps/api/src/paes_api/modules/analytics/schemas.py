from datetime import date

from pydantic import BaseModel


class DailyStat(BaseModel):
    date: date
    questions_answered: int
    correct: int
    accuracy: float | None
    minutes_practiced: float


class AnalyticsSummaryOut(BaseModel):
    current_streak_days: int
    #: Días distintos con al menos 10 preguntas respondidas, en todo el
    #: historial. Es el criterio de constancia que exigen las bases del premio,
    #: y la serie `daily` no sirve para eso: solo cubre las últimas dos semanas.
    active_days: int = 0
    #: Días seguidos, hasta hoy, terminando al menos un ensayo.
    exam_streak_days: int = 0
    #: El tramo consecutivo más largo que ha logrado. Es el que exige el premio:
    #: la racha actual castiga para siempre a quien se enfermó un día.
    best_exam_streak_days: int = 0
    #: Total de días distintos con al menos un ensayo terminado.
    exam_days: int = 0
    total_questions_answered: int
    total_correct: int
    overall_accuracy: float | None
    total_minutes_practiced: float
    daily: list[DailyStat]


class ErrorRepetido(BaseModel):
    """Un error conceptual que el alumno cometió más de una vez.

    No es "fallaste geometría". Es el razonamiento exacto que lo llevó a la
    alternativa incorrecta, escrito pregunta por pregunta en el banco: "sumó
    los exponentes en vez de multiplicarlos". Ese texto existe para las 5.586
    alternativas incorrectas y hasta ahora no se mostraba en ninguna parte.

    Es lo que separa "te equivocaste" de "sé por qué te equivocaste", y es la
    única forma de que el alumno arregle la causa en vez de repetir ejercicios.
    """

    #: El error, tal como está escrito en el banco.
    descripcion: str
    #: El enunciado de una de las preguntas donde cayó.
    #:
    #: Va porque el texto del distractor está escrito ASUMIENDO que se ve la
    #: pregunta: en una del tipo "¿cuál NO representa...?" la justificación
    #: dice "sí lo representa", y suelta se lee al revés de lo que significa.
    pregunta: str
    #: Cuántas veces cayó en él.
    veces: int
    #: Dónde vive el tema, para poder ir a estudiarlo.
    node_code: str
    node_name: str
    axis_label: str


class RitmoEje(BaseModel):
    """Cuánto se demora el alumno por pregunta en un eje."""

    axis_label: str
    #: Segundos promedio por pregunta respondida en este eje.
    segundos_por_pregunta: float
    #: Cuántas respuestas sostienen el promedio. Con pocas no se concluye nada.
    respuestas: int


class RitmoOut(BaseModel):
    """El ritmo del alumno contra el que exige la prueba real.

    En la PAES mucha gente no falla por no saber: falla porque no alcanza. Esto
    es lo que nadie entrena, y el dato para medirlo ya se estaba guardando
    (mal: ver el arreglo de time_spent_ms) desde el primer día.
    """

    #: Segundos por pregunta que concede la prueba oficial de esa asignatura.
    segundos_oficiales: float
    #: Segundos por pregunta del alumno, en promedio.
    segundos_alumno: float | None
    #: El desglose por eje, del más lento al más rápido.
    por_eje: list[RitmoEje]
    #: Cuántas preguntas quedarían sin responder al ritmo actual, o None cuando
    #: no hay datos suficientes para decirlo sin inventar.
    preguntas_sin_alcanzar: int | None
    #: Respuestas con tiempo medido que sostienen todo lo anterior.
    respuestas_medidas: int


class DiagnosticoOut(BaseModel):
    """Lo que el alumno hace mal, y por qué."""

    errores: list[ErrorRepetido]
    ritmo: RitmoOut | None
