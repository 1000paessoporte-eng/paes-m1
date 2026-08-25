"""El enfriamiento de las figuras entre un ensayo y el siguiente.

De una prueba a otra, lo que un alumno reconoce al instante es el dibujo: si
el mismo esquema de célula le cae dos ensayos seguidos, la segunda vez no
resuelve nada, se acuerda. `_figuras_recientes` responde qué figuras vio y hace
cuántos ensayos, y `_tomar` usa esa respuesta para dejarlas al final de la fila.

Lo que se fija acá: que el historial mira la FIGURA y no la pregunta, que la
postergación no es una exclusión --si no hay con qué armar, se arma igual-- y
que una pregunta sin figura no queda castigada por serlo.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from paes_api.modules.content.models import Difficulty, Question
from paes_api.modules.exam_focus.models import (
    AttemptStatus,
    ExamAttempt,
    ExamAttemptQuestion,
)
from paes_api.modules.exam_focus.service import (
    VENTANA_SIN_REPETIR,
    _figuras_recientes,
    _tomar,
)
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode, Subject
from paes_api.modules.users.models import User


def _nodo(db: Session) -> SkillNode:
    nodo = SkillNode(
        code="cie_celula_test",
        name="Célula",
        axis=SkillAxis.BIOLOGIA,
        subject=Subject.CIENCIAS,
        tier=1,
        unlock_threshold=0.75,
    )
    db.add(nodo)
    db.flush()
    return nodo


def _pregunta(db: Session, nodo: SkillNode, stem: str, figura: str | None) -> Question:
    q = Question(
        skill_node_id=nodo.id,
        difficulty=Difficulty.MEDIO,
        stem=stem,
        image_url=figura,
    )
    db.add(q)
    db.flush()
    return q


def _usuario(db: Session, email: str) -> User:
    user = User(email=email, hashed_password="x", name="Test")
    db.add(user)
    db.flush()
    return user


def _rendir(db: Session, user: User, preguntas: list[Question], cuando: datetime) -> None:
    intento = ExamAttempt(
        user_id=user.id,
        subject=Subject.CIENCIAS,
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


def test_dos_preguntas_de_la_misma_figura_cuentan_como_una_sola_vista(
    db_session: Session,
) -> None:
    """Lo que se enfría es el dibujo, no la pregunta.

    Dos preguntas distintas sobre el mismo pedigrí le repiten el pedigrí igual,
    así que ver una tiene que enfriar a la otra.
    """
    user = _usuario(db_session, "figura@milpaes.cl")
    nodo = _nodo(db_session)
    una = _pregunta(db_session, nodo, "Primera del pedigrí", "/preguntas/p.svg")
    otra = _pregunta(db_session, nodo, "Segunda del pedigrí", "/preguntas/p.svg")

    _rendir(db_session, user, [una], datetime.now(tz=UTC))

    recientes = _figuras_recientes(db_session, user.id)

    assert recientes == {"/preguntas/p.svg": 1}
    # La que nunca salió arrastra la penalización de su figura igual.
    assert _tomar([otra, una], 1, recientes) in ([otra], [una])


def test_la_figura_recien_vista_queda_ultima_en_la_fila(db_session: Session) -> None:
    user = _usuario(db_session, "orden@milpaes.cl")
    nodo = _nodo(db_session)
    vieja = _pregunta(db_session, nodo, "De figura antigua", "/preguntas/vieja.svg")
    nueva = _pregunta(db_session, nodo, "De figura reciente", "/preguntas/nueva.svg")
    ahora = datetime.now(tz=UTC)

    _rendir(db_session, user, [vieja], ahora - timedelta(days=30))
    for dias in range(VENTANA_SIN_REPETIR):
        _rendir(db_session, user, [nueva], ahora - timedelta(days=dias))

    recientes = _figuras_recientes(db_session, user.id)

    # `vieja` quedó fuera de la ventana: vuelve a competir sin castigo.
    assert "/preguntas/vieja.svg" not in recientes
    assert _tomar([nueva, vieja], 1, recientes) == [vieja]


def test_postergar_no_es_excluir(db_session: Session) -> None:
    """Si lo único que queda son figuras recién vistas, el ensayo se arma igual."""
    user = _usuario(db_session, "sinmaterial@milpaes.cl")
    nodo = _nodo(db_session)
    una = _pregunta(db_session, nodo, "Única con figura A", "/preguntas/a.svg")
    otra = _pregunta(db_session, nodo, "Única con figura B", "/preguntas/b.svg")

    _rendir(db_session, user, [una, otra], datetime.now(tz=UTC))

    recientes = _figuras_recientes(db_session, user.id)
    elegidas = _tomar([una, otra], 2, recientes)

    assert len(elegidas) == 2


def test_una_pregunta_sin_figura_no_carga_ninguna_penalizacion(
    db_session: Session,
) -> None:
    """La mayoría del banco no tiene figura y no debe perder prioridad por eso."""
    user = _usuario(db_session, "sinfigura@milpaes.cl")
    nodo = _nodo(db_session)
    con = _pregunta(db_session, nodo, "Con figura recién vista", "/preguntas/c.svg")
    sin = _pregunta(db_session, nodo, "Sin figura", None)

    _rendir(db_session, user, [con], datetime.now(tz=UTC))

    recientes = _figuras_recientes(db_session, user.id)

    assert _tomar([con, sin], 1, recientes) == [sin]
