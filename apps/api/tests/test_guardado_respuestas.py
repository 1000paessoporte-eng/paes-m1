"""El guardado de respuestas durante el ensayo.

Es el camino más caliente del producto: se llama cada vez que el alumno marca,
cambia, marca para revisar o navega. En un teléfono con red lenta las
peticiones se solapan, así que lo que se fija acá es qué pasa cuando dos
guardados de la MISMA pregunta llegan a la vez.
"""

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from paes_api.modules.content.models import Alternative, Difficulty, Question
from paes_api.modules.exam_focus.models import ExamAnswer, ExamAttempt
from paes_api.modules.exam_focus.schemas import ExamAnswerIn
from paes_api.modules.exam_focus.service import upsert_answer
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode
from paes_api.modules.users.models import User


@pytest.fixture()
def intento(db_session: Session) -> tuple[int, int]:
    """Un intento con una pregunta. Devuelve (attempt_id, question_id)."""
    user = User(email="alumna@milpaes.cl", name="Alumna", hashed_password="x")
    node = SkillNode(code="n1", name="Tema", axis=SkillAxis.NUMEROS, tier=1, unlock_threshold=0.75)
    db_session.add_all([user, node])
    db_session.flush()

    q = Question(skill_node_id=node.id, difficulty=Difficulty.FACIL, stem="2+2?")
    db_session.add(q)
    db_session.flush()
    db_session.add(Alternative(question_id=q.id, label="A", text="4", is_correct=True))

    attempt = ExamAttempt(user_id=user.id, duration_limit_seconds=8400)
    db_session.add(attempt)
    db_session.commit()
    return attempt.id, q.id


def test_guardar_dos_veces_deja_una_sola_fila(db_session: Session, intento) -> None:
    """El caso normal: el alumno cambia de opinión y vuelve a marcar."""
    attempt_id, question_id = intento

    upsert_answer(db_session, attempt_id, ExamAnswerIn(question_id=question_id, time_spent_ms=100))
    upsert_answer(db_session, attempt_id, ExamAnswerIn(question_id=question_id, time_spent_ms=900))

    filas = db_session.execute(
        select(ExamAnswer).where(ExamAnswer.attempt_id == attempt_id)
    ).scalars().all()
    assert len(filas) == 1
    assert filas[0].time_spent_ms == 900


def test_dos_guardados_simultaneos_no_duplican_ni_rompen(
    db_session: Session, intento, monkeypatch
) -> None:
    """La carrera real: dos peticiones leen "no existe" y ambas insertan.

    Antes esto dejaba DOS filas, y desde ahí el siguiente guardado de esa
    pregunta reventaba al leerlas: la pregunta quedaba inservible por el resto
    del ensayo y salía contada como omitida. Ahora la base impide el duplicado
    y el que pierde la carrera aplica su respuesta encima.

    La ventana se simula dejando ciega a la consulta previa la PRIMERA vez, que
    es exactamente lo que ve el request perdedor.
    """
    attempt_id, question_id = intento

    # El ganador de la carrera ya escribió su fila.
    upsert_answer(db_session, attempt_id, ExamAnswerIn(question_id=question_id, time_spent_ms=100))

    execute_real = db_session.execute
    llamadas = {"n": 0}

    class SinResultado:
        def scalar_one_or_none(self) -> None:
            return None

    def execute_ciego(*a, **k):
        # Solo la primera lectura miente: la del reintento tiene que ver la
        # fila que ya existe, como en la vida real.
        llamadas["n"] += 1
        if llamadas["n"] == 1:
            return SinResultado()
        return execute_real(*a, **k)

    monkeypatch.setattr(db_session, "execute", execute_ciego)
    upsert_answer(db_session, attempt_id, ExamAnswerIn(question_id=question_id, time_spent_ms=777))
    monkeypatch.setattr(db_session, "execute", execute_real)

    filas = db_session.execute(
        select(ExamAnswer).where(ExamAnswer.attempt_id == attempt_id)
    ).scalars().all()
    assert len(filas) == 1, "la carrera no puede dejar dos filas para la misma pregunta"
    # Y la respuesta que queda es la del que llegó último, no la que se perdió.
    assert filas[0].time_spent_ms == 777


def test_la_pregunta_sigue_respondible_despues_de_la_carrera(
    db_session: Session, intento, monkeypatch
) -> None:
    """El daño real del bug no era la fila de más: era que la pregunta quedaba
    rota para siempre dentro de ese ensayo."""
    attempt_id, question_id = intento
    upsert_answer(db_session, attempt_id, ExamAnswerIn(question_id=question_id, time_spent_ms=100))

    execute_real = db_session.execute
    llamadas = {"n": 0}

    class SinResultado:
        def scalar_one_or_none(self) -> None:
            return None

    def execute_ciego(*a, **k):
        llamadas["n"] += 1
        return SinResultado() if llamadas["n"] == 1 else execute_real(*a, **k)

    monkeypatch.setattr(db_session, "execute", execute_ciego)
    upsert_answer(db_session, attempt_id, ExamAnswerIn(question_id=question_id, time_spent_ms=200))
    monkeypatch.setattr(db_session, "execute", execute_real)

    # Después de la carrera, el alumno vuelve a marcar y tiene que funcionar.
    upsert_answer(db_session, attempt_id, ExamAnswerIn(question_id=question_id, time_spent_ms=555))

    total = db_session.execute(
        select(func.count(ExamAnswer.id)).where(ExamAnswer.attempt_id == attempt_id)
    ).scalar_one()
    assert total == 1
