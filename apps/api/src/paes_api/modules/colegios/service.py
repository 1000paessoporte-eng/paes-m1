"""El plan Colegios: un curso, su profesor y el avance de cada alumno."""

import secrets
from datetime import UTC, datetime

from sqlalchemy import Integer, case, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from paes_api.modules.colegios.models import Colegio
from paes_api.modules.content.models import Alternative, Question
from paes_api.modules.exam_focus.models import AttemptStatus, ExamAnswer, ExamAttempt
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.skill_tree.models import AXIS_LABELS, SkillNode
from paes_api.modules.users.models import User

#: El alfabeto del código de curso.
#:
#: Sin 0/O ni 1/I/L: el profesor lo dicta en voz alta o lo escribe en la
#: pizarra, y un cero que se lee como o manda a treinta personas a un error de
#: "código no encontrado" sin ninguna pista de por qué.
ALFABETO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
LARGO_CODIGO = 6

#: Cuántos intentos antes de rendirse. Con 31^6 combinaciones, chocar dos veces
#: seguidas es prácticamente imposible; el tope existe para no dejar un bucle
#: infinito si algo más está mal.
INTENTOS_CODIGO = 8


def _codigo_nuevo() -> str:
    return "".join(secrets.choice(ALFABETO) for _ in range(LARGO_CODIGO))


class YaTieneColegio(Exception):
    """La persona ya pertenece a un curso."""


class CodigoInvalido(Exception):
    """No existe un colegio con ese código."""


def crear_colegio(db: Session, user: User, nombre: str) -> Colegio:
    """Crea el colegio y deja a quien lo creó como profesor.

    El código se reintenta ante colisión en vez de comprobarlo antes: entre la
    consulta y el insert cabe otro registro, y la restricción única de la base
    es la única garantía real.
    """
    if user.colegio_id is not None:
        raise YaTieneColegio

    for _ in range(INTENTOS_CODIGO):
        colegio = Colegio(nombre=nombre.strip()[:160], codigo=_codigo_nuevo(), creado_por=user.id)
        db.add(colegio)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            continue
        user.colegio_id = colegio.id
        user.es_profesor = True
        db.commit()
        db.refresh(colegio)
        return colegio

    raise RuntimeError("No se pudo generar un código de curso")


def unirse(db: Session, user: User, codigo: str) -> Colegio:
    """Mete a un alumno al curso con el código que le dio su profesor.

    Quien creó el curso vuelve a entrar como PROFESOR y no como alumno. Sin
    eso, salirse era una puerta sin retorno: el panel es lo único que muestra
    el código, así que un curso cuyo profesor se sale queda sin nadie que
    pueda administrarlo ni recuperar el código para repartirlo de nuevo.
    """
    if user.colegio_id is not None:
        raise YaTieneColegio

    limpio = codigo.strip().upper()[:8]
    colegio = db.execute(
        select(Colegio).where(Colegio.codigo == limpio)
    ).scalars().first()
    if colegio is None:
        raise CodigoInvalido

    user.colegio_id = colegio.id
    user.es_profesor = colegio.creado_por == user.id
    db.commit()
    return colegio


def salir(db: Session, user: User) -> None:
    """Saca a la persona del curso sin tocar nada de lo suyo.

    Su historial, su árbol y sus ensayos son de la cuenta y no del colegio: un
    alumno que se cambia de establecimiento no pierde lo que estudió.
    """
    user.colegio_id = None
    user.es_profesor = False
    db.commit()


def resumen_alumnos(db: Session, colegio_id: int) -> list[dict]:
    """El avance de cada alumno del curso.

    Una sola consulta agregada y no una por alumno: con treinta cuentas, el
    bucle serían noventa viajes a la base para dibujar una tabla.
    """
    # El CONTEO cuenta todos los ensayos entregados, porque rendirlos es
    # actividad real y el profesor quiere verla. Los PUNTAJES solo miran los
    # representativos: un ensayo de veinte preguntas contestado en veintiún
    # segundos daría un "mejor puntaje" y un promedio que no describen a nadie,
    # y esta tabla es justamente donde el profesor decide a quién ir a buscar.
    puntaje_valido = case(
        (ExamAttempt.representativo.is_(True), ExamAttempt.estimated_score),
        else_=None,
    )
    ensayos = (
        select(
            ExamAttempt.user_id.label("uid"),
            func.count(ExamAttempt.id).label("ensayos"),
            func.max(puntaje_valido).label("mejor"),
            func.avg(puntaje_valido).label("promedio"),
            func.max(ExamAttempt.finished_at).label("ultimo"),
        )
        .where(ExamAttempt.status == AttemptStatus.SUBMITTED)
        .group_by(ExamAttempt.user_id)
        .subquery()
    )
    practicas = (
        select(
            PracticeAnswer.user_id.label("uid"),
            func.count(PracticeAnswer.id).label("respuestas"),
        )
        .group_by(PracticeAnswer.user_id)
        .subquery()
    )

    filas = db.execute(
        select(
            User.id,
            User.name,
            User.email,
            ensayos.c.ensayos,
            ensayos.c.mejor,
            ensayos.c.promedio,
            ensayos.c.ultimo,
            practicas.c.respuestas,
        )
        .outerjoin(ensayos, ensayos.c.uid == User.id)
        .outerjoin(practicas, practicas.c.uid == User.id)
        .where(User.colegio_id == colegio_id, User.es_profesor.is_(False))
        .order_by(User.name)
    ).all()

    ahora = datetime.now(UTC)
    return [
        {
            "user_id": f[0],
            "nombre": f[1],
            "email": f[2],
            "ensayos": int(f[3] or 0),
            "mejor_puntaje": int(f[4]) if f[4] is not None else None,
            "promedio": round(float(f[5])) if f[5] is not None else None,
            "ultimo_ensayo": f[6],
            "dias_sin_rendir": _dias_desde(ahora, f[6]),
            "respuestas_practica": int(f[7] or 0),
        }
        for f in filas
    ]


def _dias_desde(ahora: datetime, cuando: datetime | None) -> int | None:
    """Días transcurridos, tolerando fechas sin zona horaria.

    Postgres devuelve estas columnas con zona; SQLite --que es lo que usa la
    suite-- las devuelve sin ella, y restar una fecha con zona de una sin zona
    revienta. Se asume UTC, que es lo que la aplicación escribe siempre.
    """
    if cuando is None:
        return None
    if cuando.tzinfo is None:
        cuando = cuando.replace(tzinfo=UTC)
    return (ahora - cuando).days


def ejes_del_curso(db: Session, colegio_id: int) -> list[dict]:
    """Dónde falla el curso completo, por eje del temario.

    Es lo que un profesor no puede sacar de una tabla de puntajes: treinta
    alumnos con 600 puntos pueden estar fallando todos en el mismo eje, y eso
    decide qué se pasa la clase siguiente.

    Solo cuenta respuestas de ensayos ENTREGADOS. Un ensayo a medias tiene las
    preguntas del final sin responder, y contarlas hundiría los ejes que la
    prueba deja para el final.
    """
    filas = db.execute(
        select(
            SkillNode.axis,
            func.count(ExamAnswer.id).label("respuestas"),
            func.sum(func.cast(Alternative.is_correct, Integer)).label("correctas"),
        )
        .join(ExamAttempt, ExamAttempt.id == ExamAnswer.attempt_id)
        .join(User, User.id == ExamAttempt.user_id)
        .join(Question, Question.id == ExamAnswer.question_id)
        .join(SkillNode, SkillNode.id == Question.skill_node_id)
        .join(Alternative, Alternative.id == ExamAnswer.selected_alternative_id)
        .where(
            User.colegio_id == colegio_id,
            User.es_profesor.is_(False),
            ExamAttempt.status == AttemptStatus.SUBMITTED,
        )
        .group_by(SkillNode.axis)
        .order_by(SkillNode.axis)
    ).all()

    return [
        {
            "eje": (eje := str(f[0].value if hasattr(f[0], "value") else f[0])),
            "nombre": AXIS_LABELS.get(eje, eje.capitalize()),
            "respuestas": int(f[1] or 0),
            "porcentaje": round(100 * float(f[2] or 0) / float(f[1])) if f[1] else 0,
        }
        for f in filas
    ]
