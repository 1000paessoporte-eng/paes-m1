from datetime import date, datetime

from pydantic import BaseModel, Field

from paes_api.modules.exam_focus.models import Pace
from paes_api.modules.skill_tree.models import Subject


class CrearColegioIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=160)


class UnirseIn(BaseModel):
    codigo: str = Field(min_length=4, max_length=8)


class ColegioOut(BaseModel):
    id: int
    nombre: str
    #: El código solo se le entrega al PROFESOR. Un alumno con el código puede
    #: repartirlo fuera del curso, y entonces el panel del profesor deja de ser
    #: el de su curso.
    codigo: str | None = None
    es_profesor: bool
    alumnos: int


class AlumnoOut(BaseModel):
    user_id: int
    nombre: str
    #: El correo solo lo ve el profesor de ese curso: es el dato que le permite
    #: reconocer a quién corresponde cada fila.
    email: str
    ensayos: int
    mejor_puntaje: int | None
    promedio: int | None
    ultimo_ensayo: datetime | None
    #: Días desde el último ensayo entregado. `null` si nunca rindió uno.
    #:
    #: Viaja calculado desde el servidor porque leer el reloj durante el render
    #: --de cliente o de servidor-- es una impureza que React prohíbe: el mismo
    #: componente daría un número distinto en cada dibujado.
    dias_sin_rendir: int | None
    respuestas_practica: int
    #: Días desde la última respuesta en Modo Práctica. `null` si nunca
    #: practicó. Va junto al anterior porque "sin actividad" son los dos: quien
    #: practica todos los días y no rinde ensayos no es alguien perdido.
    dias_sin_practicar: int | None = None


class EjeCursoOut(BaseModel):
    """Cómo va el curso completo en un eje del temario."""

    eje: str
    #: El nombre como aparece en el temario del DEMRE. Viaja resuelto desde
    #: acá para que el frontend no tenga que mantener su propia copia de los
    #: trece ejes de las cinco pruebas.
    nombre: str
    porcentaje: int
    respuestas: int


class CrearEnsayoIn(BaseModel):
    titulo: str = Field(min_length=2, max_length=160)
    subject: Subject
    fecha: date
    question_count: int = Field(default=65, ge=5, le=200)
    pace: Pace = Pace.OFICIAL


class EnsayoProgramadoOut(BaseModel):
    id: int
    titulo: str
    subject: Subject
    pace: Pace
    question_count: int
    fecha: date
    #: Cuántos del curso ya lo rindieron. Solo se llena para el profesor.
    rendido_por: int | None = None
    #: Si YO ya lo rendí. Solo se llena para el alumno.
    lo_rendi: bool | None = None


class ColegioAdminOut(BaseModel):
    """Un curso visto desde el panel de administración."""

    id: int
    nombre: str
    codigo: str
    alumnos: int
    plan_hasta: date | None
    creado_en: datetime


class PlanColegioIn(BaseModel):
    #: Hasta cuándo queda pagado. `null` corta el plan.
    plan_hasta: date | None = None
