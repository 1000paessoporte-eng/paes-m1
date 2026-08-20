"""Repaso inteligente: las preguntas que falló vuelven hasta que las domina.

El problema que resuelve: hoy fallar una pregunta no tiene ninguna
consecuencia. El alumno lee la explicación, cierra el ensayo, y con 1.862
preguntas sorteadas al azar no la vuelve a ver nunca. Estudia lo que le toca,
no lo que le falta.

El método es una escalera de intervalos (Leitner), no un SM-2 con factores de
facilidad. Es deliberado: la escalera se puede explicar en una frase --"si la
aciertas vuelve más adelante, si la fallas vuelve mañana"-- y el alumno puede
predecir qué le va a tocar. Un algoritmo que nadie entiende se siente
arbitrario, y de lo arbitrario la gente desconfía.
"""

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from paes_api.modules.content.models import Alternative, Question
from paes_api.modules.exam_focus.models import ExamAnswer, ExamAttempt
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.repaso.models import RepasoItem

#: Cuántos días espera una pregunta, según el peldaño en que QUEDA.
#:
#: Se lee así: el peldaño 0 es el de una pregunta recién fallada, y espera 1
#: día. Cada acierto la sube un peldaño --3 días, 7, 16, 35-- y al acertarla en
#: el último sale de la cola: cinco aciertos repartidos en dos meses es tan
#: cerca de "aprendido" como se puede medir sin adivinar.
#:
#: Crecen rápido a propósito. Repasar algo que ya se sabe es tiempo que no se
#: gastó en lo que no se sabe.
ESCALERA_DIAS: tuple[int, ...] = (1, 3, 7, 16, 35)

#: Cuántas preguntas trae una sesión, como mucho.
#:
#: Alguien que rindió tres ensayos malos puede acumular 90 preguntas
#: pendientes, y una cola de 90 no se empieza: se cierra. Doce es una sesión de
#: unos quince minutos, que es lo que cabe en un día de clases.
LIMITE_SESION = 12


def _hoy() -> date:
    return datetime.now(UTC).date()


def _falladas_vigentes(db: Session, user_id: int) -> list[int]:
    """Las preguntas cuya ÚLTIMA respuesta fue incorrecta.

    "Última" y no "alguna": si la falló en marzo y la acertó en mayo, ya no es
    material de repaso, y arrastrarla a la cola gastaría la sesión en algo que
    el alumno resolvió solo.

    Junta ensayo y práctica porque para el alumno son la misma pregunta. Se
    resuelve en Python en vez de con una ventana en SQL: son unos cientos de
    filas por usuario y la versión legible es la que vamos a poder corregir.
    """
    respuestas: dict[int, tuple[datetime, bool]] = {}

    filas_ensayo = db.execute(
        select(ExamAnswer.question_id, ExamAnswer.answered_at, Alternative.is_correct)
        .join(ExamAttempt, ExamAttempt.id == ExamAnswer.attempt_id)
        .join(Alternative, Alternative.id == ExamAnswer.selected_alternative_id)
        .where(ExamAttempt.user_id == user_id, ExamAnswer.answered_at.is_not(None))
    ).all()
    for question_id, answered_at, is_correct in filas_ensayo:
        previa = respuestas.get(question_id)
        if previa is None or answered_at > previa[0]:
            respuestas[question_id] = (answered_at, is_correct)

    filas_practica = db.execute(
        select(
            PracticeAnswer.question_id, PracticeAnswer.answered_at, PracticeAnswer.is_correct
        ).where(PracticeAnswer.user_id == user_id)
    ).all()
    for question_id, answered_at, is_correct in filas_practica:
        previa = respuestas.get(question_id)
        if previa is None or answered_at > previa[0]:
            respuestas[question_id] = (answered_at, is_correct)

    return [qid for qid, (_, correcta) in respuestas.items() if not correcta]


def asegurar_items(db: Session, user_id: int) -> int:
    """Mete a la cola las preguntas falladas que todavía no están, y devuelve
    cuántas agregó.

    Se ejecuta al consultar, no al responder un ensayo. Así el repaso nace
    lleno para quien ya venía usando la plataforma --de otro modo la pantalla
    estrenaría vacía justo para los usuarios que más material acumulado
    tienen-- y no hay que tocar el cierre del ensayo, que es código con
    usuarios encima.
    """
    falladas = set(_falladas_vigentes(db, user_id))
    if not falladas:
        return 0

    ya_estan = set(
        db.execute(select(RepasoItem.question_id).where(RepasoItem.user_id == user_id))
        .scalars()
        .all()
    )
    nuevas = falladas - ya_estan
    if not nuevas:
        return 0

    hoy = _hoy()
    for question_id in nuevas:
        # Entran vencidas: son preguntas que ya falló, no hay nada que esperar.
        db.add(
            RepasoItem(
                user_id=user_id, question_id=question_id, nivel=0, proxima_fecha=hoy
            )
        )
    db.commit()
    return len(nuevas)


def pendientes(db: Session, user_id: int, limite: int = LIMITE_SESION) -> list[RepasoItem]:
    """Lo que toca hoy: vencidas primero, y de las vencidas las más falladas.

    El orden importa. Una pregunta que ya falló tres veces dentro del repaso es
    la que de verdad no entiende, y si la sesión se corta a las doce tiene que
    quedar dentro.
    """
    return list(
        db.execute(
            select(RepasoItem)
            .where(
                RepasoItem.user_id == user_id,
                RepasoItem.proxima_fecha.is_not(None),
                RepasoItem.proxima_fecha <= _hoy(),
            )
            .order_by(
                RepasoItem.veces_fallada.desc(),
                RepasoItem.proxima_fecha.asc(),
                RepasoItem.id.asc(),
            )
            .limit(limite)
        )
        .scalars()
        .all()
    )


def registrar_respuesta(item: RepasoItem, acerto: bool) -> None:
    """Mueve la pregunta en la escalera. No hace commit: lo hace quien llama.

    Al fallar vuelve al primer peldaño, no al anterior. Es más duro de lo que
    haría un SM-2, y es a propósito: acá adentro no hay preguntas nuevas, todas
    son preguntas que ya falló al menos una vez, así que volver a fallarla es
    señal de que el tema no está, no de que tuvo un mal día.
    """
    item.veces_vista += 1
    item.actualizado_en = datetime.now(UTC)

    if not acerto:
        item.veces_fallada += 1
        item.nivel = 0
        # Mañana, no hoy: dentro de la misma sesión el alumno la recordaría de
        # memoria en vez de resolverla, y eso no es saber la pregunta.
        item.proxima_fecha = _hoy() + _dias(0)
        return

    item.nivel += 1
    if item.nivel >= len(ESCALERA_DIAS):
        # Acertó en el último peldaño: sale de la cola para siempre.
        item.proxima_fecha = None
        return
    item.proxima_fecha = _hoy() + _dias(item.nivel)


def _dias(nivel: int) -> timedelta:
    return timedelta(days=ESCALERA_DIAS[nivel])


def resumen(db: Session, user_id: int) -> dict:
    """Los tres números de la tarjeta: qué toca hoy, qué está en curso, qué ya
    dominó."""
    items = list(
        db.execute(select(RepasoItem).where(RepasoItem.user_id == user_id)).scalars().all()
    )
    hoy = _hoy()
    con_fecha = [i for i in items if i.proxima_fecha is not None]
    futuras = [i.proxima_fecha for i in con_fecha if i.proxima_fecha > hoy]
    return {
        "pendientes_hoy": sum(1 for i in con_fecha if i.proxima_fecha <= hoy),
        "en_repaso": len(con_fecha),
        "dominadas": len(items) - len(con_fecha),
        "proxima_fecha": min(futuras) if futuras else None,
    }


def cargar_pregunta(db: Session, question_id: int) -> Question | None:
    return db.execute(
        select(Question)
        .where(Question.id == question_id)
        .options(selectinload(Question.alternatives), selectinload(Question.skill_node))
    ).scalar_one_or_none()
