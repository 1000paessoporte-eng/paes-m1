from datetime import datetime

from pydantic import BaseModel, Field

from paes_api.modules.content.models import Difficulty
from paes_api.modules.exam_focus.models import AttemptStatus, Pace
from paes_api.modules.skill_tree.models import Subject


class ExamAlternativeOut(BaseModel):
    """Alternativa durante el examen: SIN is_correct ni
    distractor_justification. Esos datos solo se exponen después de
    submit (revisión de respuestas)."""

    id: int
    label: str
    text: str


class PassageOut(BaseModel):
    """Texto base de una pregunta de Competencia Lectora."""

    id: int
    title: str
    body: str
    kind: str
    source_note: str | None = None


class ExamQuestionOut(BaseModel):
    id: int
    skill_node_id: int
    skill_node_name: str = ""
    axis: str = ""
    difficulty: Difficulty
    stem: str
    image_url: str | None = None
    #: Solo en Competencia Lectora: el texto sobre el que trata la pregunta.
    #: Varias preguntas del mismo ensayo comparten el mismo pasaje.
    passage: PassageOut | None = None
    #: Cuántos segundos conviene dedicarle a ESTA pregunta.
    #:
    #: No todas valen lo mismo: una difícil pesa más que una fácil, y en
    #: Competencia Lectora la primera de cada texto carga con leerlo. La suma
    #: de todos los sugeridos es exactamente la duración del intento, así que
    #: no se promete tiempo que la prueba no da.
    suggested_seconds: int = 0
    #: Si el alumno YA respondió mal esta pregunta antes, en otro ensayo o
    #: practicando.
    #:
    #: Con un banco de miles de preguntas sorteadas al azar, reencontrarse con
    #: una que uno falló es la mejor oportunidad de aprendizaje que da la
    #: plataforma, y pasaba completamente desapercibida. Se avisa DENTRO del
    #: ensayo, que es el único momento en que el alumno la tiene al frente.
    fallada_antes: bool = False
    alternatives: list[ExamAlternativeOut]


class ExamAnswerState(BaseModel):
    selected_alternative_id: int | None = None
    time_spent_ms: int = 0
    flagged: bool = False


class AxisOptionOut(BaseModel):
    """Un eje temático y cuántas preguntas hay disponibles en el banco."""

    axis: str
    label: str
    available: int


class ExamOptionsOut(BaseModel):
    """Todo lo que la pantalla de configuración necesita para armarse."""

    subject: Subject
    axes: list[AxisOptionOut]
    total_available: int
    seconds_per_question: float
    official_questions: int
    official_duration_min: int


class ExamConfigIn(BaseModel):
    """Configuración elegida por el estudiante antes de comenzar."""

    subject: Subject = Subject.M1
    question_count: int = Field(default=20, ge=1, le=200)
    pace: Pace = Pace.OFICIAL
    #: Ejes seleccionados. Lista vacía significa "todos", repartidos proporcionalmente.
    axes: list[str] = Field(default_factory=list)


class ExamConfigOut(BaseModel):
    subject: Subject
    question_count: int
    pace: Pace
    axes: list[str]


class RepasoOut(BaseModel):
    """Sugerencia para el boton "Ensayo de repaso": los ejes de los nodos
    donde el estudiante rinde peor, reusando el mismo progreso del Arbol de
    Habilidades. has_data en False significa que todavia no hay suficientes
    respuestas para sugerir nada (usuario nuevo)."""

    has_data: bool
    axes: list[str]
    axis_labels: list[str]


class ExamStartOut(BaseModel):
    attempt_id: int
    started_at: datetime
    duration_limit_seconds: int
    config: ExamConfigOut
    questions: list[ExamQuestionOut]


class ExamStateOut(ExamStartOut):
    status: AttemptStatus
    answers: dict[int, ExamAnswerState]


class ExamAnswerIn(BaseModel):
    question_id: int
    selected_alternative_id: int | None = None
    time_spent_ms: int = 0
    flagged: bool = False


class BreakdownItemOut(BaseModel):
    """Desempeño agrupado por eje, nodo o dificultad."""

    name: str
    #: El código del nodo, SOLO en el desglose por nodo. Es lo que convierte el
    #: desglose en algo que se puede pulsar: con él la pantalla de resultados
    #: enlaza a la lección (`/aprender/{code}`) y a la práctica
    #: (`/practicar/{code}`) del tema que salió peor. Los ejes y las
    #: dificultades no son nodos y no tienen página propia, así que van en None.
    code: str | None = None
    correct: int
    incorrect: int
    omitted: int
    total: int
    percentage: int


class ExamResultOut(BaseModel):
    attempt_id: int
    status: AttemptStatus
    total_questions: int
    answered: int
    correct: int
    incorrect: int
    omitted: int
    estimated_score: int
    elapsed_seconds: int
    duration_limit_seconds: int
    #: False si se contestó tan rápido que no da tiempo ni de leer. El ensayo
    #: vale igual --se corrige y se revisa igual-- pero no entra al mejor
    #: puntaje ni a los promedios, porque ahí un número falso engaña.
    representativo: bool = True
    by_axis: list[BreakdownItemOut]
    by_difficulty: list[BreakdownItemOut]
    by_node: list[BreakdownItemOut]


class ExamAttemptSummary(BaseModel):
    attempt_id: int
    started_at: datetime
    finished_at: datetime | None = None
    status: AttemptStatus
    subject: Subject
    total_questions: int
    answered: int
    correct: int
    estimated_score: int | None = None
    elapsed_seconds: int
    duration_limit_seconds: int
    #: False si se contestó tan rápido que no da tiempo ni de leer. El ensayo
    #: vale igual --se corrige y se revisa igual-- pero no entra al mejor
    #: puntaje ni a los promedios, porque ahí un número falso engaña.
    representativo: bool = True
    pace: Pace
    axes: list[str]


class ReviewAlternativeOut(BaseModel):
    """Alternativa en la revisión post-examen: SÍ incluye is_correct y
    distractor_justification — el porqué de cada error."""

    id: int
    label: str
    text: str
    is_correct: bool
    distractor_justification: str | None = None
    selected: bool


class ReviewQuestionOut(BaseModel):
    id: int
    stem: str
    #: La figura de la pregunta, si la tiene. Va también en la revisión: sin
    #: ella, la explicación de una pregunta que se apoya en un gráfico habla de
    #: algo que ya no está a la vista.
    image_url: str | None = None
    #: Desarrollo de por qué la respuesta correcta lo es. Es lo que se muestra
    #: al revisar el ensayo.
    explanation: str | None = None
    difficulty: Difficulty
    skill_node_id: int
    skill_node_code: str
    skill_node_name: str
    axis: str
    time_spent_ms: int
    answered_correctly: bool | None
    alternatives: list[ReviewAlternativeOut]


class NodeDiagnosisOut(BaseModel):
    skill_node_id: int
    skill_node_code: str
    skill_node_name: str
    axis: str
    total: int
    correct: int
    accuracy: float


class ExamReviewOut(BaseModel):
    attempt_id: int
    status: AttemptStatus
    questions: list[ReviewQuestionOut]
    node_diagnosis: list[NodeDiagnosisOut]
