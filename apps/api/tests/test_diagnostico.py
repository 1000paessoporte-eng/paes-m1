"""El diagnóstico: qué hace mal el alumno y por qué.

Lo que se fija acá es sobre todo cuándo NO hablar. Una pantalla que le dice a
alguien "tienes un problema con las potencias" apoyada en un error suelto, o
"vas lento" apoyada en tres respuestas, es peor que una pantalla vacía: hace
que deje de creerle al resto.
"""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from paes_api.modules.content.models import Alternative, Difficulty, Question
from paes_api.modules.exam_focus.models import AttemptStatus, ExamAnswer, ExamAttempt
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode
from paes_api.modules.users.models import User


@pytest.fixture()
def escenario(db_session: Session):
    """Un nodo, dos preguntas y un intento donde poder registrar respuestas."""
    node = SkillNode(
        code="pot_raices", name="Potencias y raíces", axis=SkillAxis.NUMEROS,
        tier=1, unlock_threshold=0.75,
    )
    db_session.add(node)
    db_session.flush()

    preguntas = []
    for i in range(3):
        q = Question(skill_node_id=node.id, difficulty=Difficulty.FACIL, stem=f"P{i}")
        db_session.add(q)
        db_session.flush()
        mala = Alternative(
            question_id=q.id, label="A", text="mal", is_correct=False,
            distractor_justification="Sumó los exponentes en vez de multiplicarlos.",
        )
        buena = Alternative(question_id=q.id, label="B", text="bien", is_correct=True)
        db_session.add_all([mala, buena])
        db_session.flush()
        preguntas.append((q, mala, buena))
    db_session.commit()
    return node, preguntas


def _preguntas_extra(db_session: Session, node: SkillNode, n: int):
    """n preguntas con su alternativa correcta.

    Cada respuesta necesita SU pregunta: desde el PR #81 la base impide dos
    respuestas para el mismo par (intento, pregunta), que es justo lo que
    arregló la carrera que dejaba preguntas inservibles.
    """
    salida = []
    for i in range(n):
        q = Question(skill_node_id=node.id, difficulty=Difficulty.FACIL, stem=f"extra{i}")
        db_session.add(q)
        db_session.flush()
        buena = Alternative(question_id=q.id, label="A", text="ok", is_correct=True)
        db_session.add(buena)
        db_session.flush()
        salida.append((q, buena))
    db_session.commit()
    return salida


def _intento(db_session: Session, email: str) -> ExamAttempt:
    user = db_session.query(User).filter(User.email == email).one()
    a = ExamAttempt(
        user_id=user.id, duration_limit_seconds=8400, status=AttemptStatus.SUBMITTED
    )
    db_session.add(a)
    db_session.commit()
    return a


def test_un_error_suelto_tambien_se_muestra(
    client: TestClient, db_session: Session, register_user, escenario
) -> None:
    """No se exige repetición para hablar, y eso se midió sobre el banco real:
    5.586 distractores tienen 5.284 textos distintos, así que pedir dos
    apariciones dejaba la sección vacía casi siempre. El valor está en mostrar
    el razonamiento, que hoy no se ve en ninguna pantalla."""
    headers, _ = register_user(email="uno@milpaes.cl")
    _node, preguntas = escenario
    a = _intento(db_session, "uno@milpaes.cl")
    q, mala, _ = preguntas[0]
    db_session.add(
        ExamAnswer(attempt_id=a.id, question_id=q.id, selected_alternative_id=mala.id,
                   answered_at=datetime.now(UTC))
    )
    db_session.commit()

    errores = client.get("/api/analytics/diagnostico", headers=headers).json()["errores"]
    assert len(errores) == 1
    assert errores[0]["veces"] == 1
    assert "exponentes" in errores[0]["descripcion"]


def test_el_mismo_error_dos_veces_si_se_reporta(
    client: TestClient, db_session: Session, register_user, escenario
) -> None:
    """Y se agrupa por el RAZONAMIENTO, no por la pregunta: el mismo error
    aparece en preguntas distintas y lo que hay que arreglar es el error."""
    headers, _ = register_user(email="dos@milpaes.cl")
    _node, preguntas = escenario
    a = _intento(db_session, "dos@milpaes.cl")
    for q, mala, _ in preguntas[:3]:
        db_session.add(
            ExamAnswer(attempt_id=a.id, question_id=q.id, selected_alternative_id=mala.id,
                       answered_at=datetime.now(UTC))
        )
    db_session.commit()

    errores = client.get("/api/analytics/diagnostico", headers=headers).json()["errores"]
    assert len(errores) == 1, "tres preguntas, un solo error conceptual"
    assert errores[0]["veces"] == 3
    assert "exponentes" in errores[0]["descripcion"]
    assert errores[0]["node_code"] == "pot_raices"
    assert errores[0]["axis_label"] == "Números"


def test_acertar_no_cuenta_como_error(
    client: TestClient, db_session: Session, register_user, escenario
) -> None:
    headers, _ = register_user(email="bien@milpaes.cl")
    _node, preguntas = escenario
    a = _intento(db_session, "bien@milpaes.cl")
    for q, _mala, buena in preguntas:
        db_session.add(
            ExamAnswer(attempt_id=a.id, question_id=q.id, selected_alternative_id=buena.id,
                       answered_at=datetime.now(UTC))
        )
    db_session.commit()

    assert client.get("/api/analytics/diagnostico", headers=headers).json()["errores"] == []


def test_sin_datos_suficientes_no_se_habla_de_ritmo(
    client: TestClient, db_session: Session, register_user, escenario
) -> None:
    """Tres respuestas no son un ritmo. Proyectar sobre eso es inventar: ya
    pasó en este proyecto, extrapolar cuatro ensayos del mismo día daba -2.760
    puntos al mes."""
    headers, _ = register_user(email="poco@milpaes.cl")
    _node, preguntas = escenario
    a = _intento(db_session, "poco@milpaes.cl")
    for q, _m, buena in preguntas:
        db_session.add(
            ExamAnswer(attempt_id=a.id, question_id=q.id, selected_alternative_id=buena.id,
                       time_spent_ms=90_000, answered_at=datetime.now(UTC))
        )
    db_session.commit()

    assert client.get("/api/analytics/diagnostico", headers=headers).json()["ritmo"] is None


def test_con_datos_el_ritmo_se_compara_con_el_oficial(
    client: TestClient, db_session: Session, register_user, escenario
) -> None:
    """M1 da 140 min para 65 preguntas: 129,2 s por pregunta. Un alumno que se
    demora 200 s va lento y no alcanzaría a terminar."""
    headers, _ = register_user(email="lento@milpaes.cl")
    node, _preguntas = escenario
    a = _intento(db_session, "lento@milpaes.cl")
    # 25 respuestas: por encima del mínimo para poder concluir.
    for q, buena in _preguntas_extra(db_session, node, 25):
        db_session.add(
            ExamAnswer(attempt_id=a.id, question_id=q.id, selected_alternative_id=buena.id,
                       time_spent_ms=200_000, answered_at=datetime.now(UTC))
        )
    db_session.commit()

    ritmo = client.get("/api/analytics/diagnostico", headers=headers).json()["ritmo"]
    assert ritmo is not None
    assert ritmo["segundos_alumno"] == 200.0
    assert round(ritmo["segundos_oficiales"]) == 129
    assert ritmo["respuestas_medidas"] == 25
    # A 200 s por pregunta, en 140 minutos alcanza a 42 de 65.
    assert ritmo["preguntas_sin_alcanzar"] == 23


def test_el_que_va_a_tiempo_no_deja_preguntas_fuera(
    client: TestClient, db_session: Session, register_user, escenario
) -> None:
    headers, _ = register_user(email="rapido@milpaes.cl")
    node, _preguntas = escenario
    a = _intento(db_session, "rapido@milpaes.cl")
    for q, buena in _preguntas_extra(db_session, node, 25):
        db_session.add(
            ExamAnswer(attempt_id=a.id, question_id=q.id, selected_alternative_id=buena.id,
                       time_spent_ms=60_000, answered_at=datetime.now(UTC))
        )
    db_session.commit()

    ritmo = client.get("/api/analytics/diagnostico", headers=headers).json()["ritmo"]
    assert ritmo["preguntas_sin_alcanzar"] == 0


def test_la_pregunta_saltada_no_cuenta_para_el_ritmo(
    client: TestClient, db_session: Session, register_user, escenario
) -> None:
    """Una pregunta que se dejó en blanco no dice nada sobre cuánto se demora."""
    headers, _ = register_user(email="blanco@milpaes.cl")
    node, _preguntas = escenario
    a = _intento(db_session, "blanco@milpaes.cl")
    for q, _buena in _preguntas_extra(db_session, node, 25):
        db_session.add(
            ExamAnswer(attempt_id=a.id, question_id=q.id, selected_alternative_id=None,
                       time_spent_ms=200_000, answered_at=datetime.now(UTC))
        )
    db_session.commit()

    assert client.get("/api/analytics/diagnostico", headers=headers).json()["ritmo"] is None
