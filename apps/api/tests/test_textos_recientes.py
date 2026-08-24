"""El historial de textos que alimenta el enfriamiento de Competencia Lectora.

`_textos_recientes` responde qué textos vio el estudiante y hace cuántos
ensayos. De esa respuesta depende que un texto de novecientas palabras no
vuelva a caerle en el ensayo siguiente, así que conviene fijar sus tres
decisiones: cuántos ensayos hacia atrás mira, qué pasa cuando un texto salió
en varios, y que el historial es de cada estudiante y no del sistema.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from paes_api.modules.content.models import Difficulty, Question, ReadingPassage
from paes_api.modules.exam_focus.models import (
    AttemptStatus,
    ExamAttempt,
    ExamAttemptQuestion,
)
from paes_api.modules.exam_focus.service import (
    VENTANA_SIN_REPETIR,
    _textos_recientes,
)
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode, Subject
from paes_api.modules.users.models import User


def _montar_banco(db: Session, cuantos_textos: int) -> list[Question]:
    """Un texto por pregunta, que es todo lo que este historial necesita."""
    nodo = SkillNode(
        code="lec_localizar_test",
        name="Localizar",
        axis=SkillAxis.NUMEROS,
        subject=Subject.LECTORA,
        tier=1,
        unlock_threshold=0.75,
    )
    db.add(nodo)
    db.flush()

    preguntas = []
    for n in range(1, cuantos_textos + 1):
        texto = ReadingPassage(title=f"Texto {n}", body="...", kind="no_literario")
        db.add(texto)
        db.flush()
        pregunta = Question(
            skill_node_id=nodo.id,
            difficulty=Difficulty.FACIL,
            stem=f"Pregunta del texto {n}",
            passage_id=texto.id,
        )
        db.add(pregunta)
        preguntas.append(pregunta)
    db.flush()
    return preguntas


def _usuario(db: Session, email: str) -> User:
    user = User(email=email, hashed_password="x", name="Test")
    db.add(user)
    db.flush()
    return user


def _rendir(db: Session, user: User, preguntas: list[Question], cuando: datetime) -> None:
    intento = ExamAttempt(
        user_id=user.id,
        subject=Subject.LECTORA,
        status=AttemptStatus.SUBMITTED,
        started_at=cuando,
    )
    db.add(intento)
    db.flush()
    db.add_all(
        ExamAttemptQuestion(attempt_id=intento.id, question_id=q.id, position=i)
        for i, q in enumerate(preguntas)
    )
    db.flush()


def test_el_ensayo_mas_reciente_es_el_de_antiguedad_uno(db_session: Session) -> None:
    user = _usuario(db_session, "reciente@milpaes.cl")
    preguntas = _montar_banco(db_session, 4)
    ahora = datetime.now(tz=UTC)

    _rendir(db_session, user, preguntas[:2], ahora - timedelta(days=2))
    _rendir(db_session, user, preguntas[2:], ahora)

    recientes = _textos_recientes(db_session, user.id)

    assert recientes[preguntas[2].passage_id] == 1
    assert recientes[preguntas[3].passage_id] == 1
    assert recientes[preguntas[0].passage_id] == 2
    assert recientes[preguntas[1].passage_id] == 2


def test_un_texto_que_salio_dos_veces_cuenta_por_la_vez_mas_reciente(
    db_session: Session,
) -> None:
    """Si no, un texto leído ayer heredaría la antigüedad de hace un mes."""
    user = _usuario(db_session, "repetido@milpaes.cl")
    preguntas = _montar_banco(db_session, 2)
    ahora = datetime.now(tz=UTC)

    _rendir(db_session, user, preguntas, ahora - timedelta(days=10))
    _rendir(db_session, user, [preguntas[0]], ahora - timedelta(days=1))

    recientes = _textos_recientes(db_session, user.id)

    assert recientes[preguntas[0].passage_id] == 1
    assert recientes[preguntas[1].passage_id] == 2


def test_lo_anterior_a_la_ventana_no_entra(db_session: Session) -> None:
    """Más allá de la ventana el texto vuelve a estar disponible sin castigo."""
    user = _usuario(db_session, "ventana@milpaes.cl")
    preguntas = _montar_banco(db_session, VENTANA_SIN_REPETIR + 2)
    ahora = datetime.now(tz=UTC)

    # Un ensayo por texto, del más antiguo al más nuevo.
    for n, pregunta in enumerate(preguntas):
        _rendir(db_session, user, [pregunta], ahora - timedelta(days=len(preguntas) - n))

    recientes = _textos_recientes(db_session, user.id)

    assert len(recientes) == VENTANA_SIN_REPETIR
    # Los dos primeros quedaron fuera de la ventana.
    assert preguntas[0].passage_id not in recientes
    assert preguntas[1].passage_id not in recientes
    assert recientes[preguntas[-1].passage_id] == 1


def test_el_historial_es_de_cada_estudiante(db_session: Session) -> None:
    user = _usuario(db_session, "propio@milpaes.cl")
    otro = _usuario(db_session, "ajeno@milpaes.cl")
    preguntas = _montar_banco(db_session, 2)
    ahora = datetime.now(tz=UTC)

    _rendir(db_session, otro, preguntas, ahora)

    assert _textos_recientes(db_session, user.id) == {}
    assert len(_textos_recientes(db_session, otro.id)) == 2


def test_un_ensayo_de_matematica_no_ensucia_el_historial(db_session: Session) -> None:
    """El enfriamiento es de textos: un ensayo de M1 no tiene ninguno."""
    user = _usuario(db_session, "matematica@milpaes.cl")
    preguntas = _montar_banco(db_session, 2)
    intento = ExamAttempt(
        user_id=user.id,
        subject=Subject.M1,
        status=AttemptStatus.SUBMITTED,
        started_at=datetime.now(tz=UTC),
    )
    db_session.add(intento)
    db_session.flush()
    db_session.add_all(
        ExamAttemptQuestion(attempt_id=intento.id, question_id=q.id, position=i)
        for i, q in enumerate(preguntas)
    )
    db_session.flush()

    assert _textos_recientes(db_session, user.id) == {}
