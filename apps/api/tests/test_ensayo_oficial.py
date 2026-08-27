"""El ensayo en formato oficial y el registro de salidas de la página.

Un ensayo de veinte preguntas en media hora entrena contenido. No entrena
rendir dos horas y veinte seguidas, que es la otra mitad de lo que la PAES
mide: sostener la atención, administrar el tiempo y no quedarse pegado en la
pregunta 12. Por eso el formato oficial no es una configuración más, es un modo
aparte: la prueba completa, todos los ejes y la duración exacta del DEMRE.

Las salidas de la página se registran pero no invalidan nada. Una notificación
entrante no es hacer trampa, y castigarla sería castigar a quien rinde desde el
celular. El dato se guarda porque le sirve al estudiante: descubrir que salió
once veces dice más sobre cómo le va a ir que el puntaje mismo.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from paes_api.modules.content.models import Alternative, Difficulty, Question
from paes_api.modules.exam_focus import scoring, service
from paes_api.modules.exam_focus.models import AttemptStatus, ExamAttempt, Pace
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode, Subject


def _banco(db: Session, cuantas: int = 70) -> None:
    """Preguntas suficientes para armar una prueba completa de M1."""
    node = SkillNode(
        code="n_oficial",
        name="Tema",
        axis=SkillAxis.NUMEROS,
        subject=Subject.M1,
        tier=1,
        unlock_threshold=0.75,
    )
    db.add(node)
    db.flush()
    for i in range(cuantas):
        q = Question(skill_node_id=node.id, difficulty=Difficulty.MEDIO, stem=f"Of{i}")
        db.add(q)
        db.flush()
        db.add_all(
            [
                Alternative(question_id=q.id, label="A", text="ok", is_correct=True),
                Alternative(
                    question_id=q.id,
                    label="B",
                    text="mal",
                    is_correct=False,
                    distractor_justification="Se equivocó.",
                ),
            ]
        )
    db.commit()


def test_el_oficial_trae_la_prueba_completa_y_dura_lo_que_dura_la_prueba(
    client: TestClient, db_session: Session, register_user
) -> None:
    _banco(db_session)
    headers, _ = register_user(email="oficial@milpaes.cl")

    inicio = client.post(
        "/api/exam/start", json={"subject": "m1", "oficial": True}, headers=headers
    ).json()

    esperado = scoring.SCORING_BY_SUBJECT[Subject.M1]
    assert len(inicio["questions"]) == esperado.preguntas_oficiales
    assert inicio["duration_limit_seconds"] == esperado.duracion_oficial_min * 60
    assert inicio["config"]["oficial"] is True


def test_el_oficial_ignora_la_configuracion_a_medida(
    client: TestClient, db_session: Session, register_user
) -> None:
    """El formato no es negociable: en eso consiste llamarlo oficial.

    Alguien podría pedir un "oficial" de cinco preguntas en modo relajado y
    quedarse con el sello sin haber rendido la prueba. El servidor descarta lo
    que venga en `question_count`, `pace` y `axes`.
    """
    _banco(db_session)
    headers, _ = register_user(email="oficial2@milpaes.cl")

    inicio = client.post(
        "/api/exam/start",
        json={
            "subject": "m1",
            "oficial": True,
            "question_count": 5,
            "pace": "relajado",
            "axes": ["numeros"],
        },
        headers=headers,
    ).json()

    assert len(inicio["questions"]) == 65
    assert inicio["config"]["pace"] == Pace.OFICIAL.value
    assert inicio["config"]["axes"] == []


def test_un_ensayo_normal_sigue_siendo_configurable(
    client: TestClient, db_session: Session, register_user
) -> None:
    """El modo oficial se suma, no reemplaza: el ensayo a medida no cambia."""
    _banco(db_session)
    headers, _ = register_user(email="medida@milpaes.cl")

    inicio = client.post(
        "/api/exam/start",
        json={"subject": "m1", "question_count": 8, "pace": "exigente"},
        headers=headers,
    ).json()

    assert len(inicio["questions"]) == 8
    assert inicio["config"]["oficial"] is False


def test_las_salidas_se_acumulan_y_viajan_en_el_resultado(
    client: TestClient, db_session: Session, register_user
) -> None:
    _banco(db_session, cuantas=6)
    headers, _ = register_user(email="salidas@milpaes.cl")
    aid = client.post(
        "/api/exam/start",
        json={"subject": "m1", "question_count": 6},
        headers=headers,
    ).json()["attempt_id"]

    for segundos in (12, 30):
        cuerpo = client.post(
            f"/api/exam/{aid}/salida", json={"segundos": segundos}, headers=headers
        ).json()
    assert cuerpo == {"salidas": 2, "segundos_fuera": 42}

    resultado = client.post(f"/api/exam/{aid}/submit", headers=headers).json()
    assert resultado["salidas"] == 2
    assert resultado["segundos_fuera"] == 42


def test_una_salida_larguisima_se_recorta(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Una pestaña abierta toda la noche no son ocho horas fuera de un ensayo
    de dos: sin tope, el resultado diría un disparate."""
    _banco(db_session, cuantas=6)
    headers, _ = register_user(email="noche@milpaes.cl")
    aid = client.post(
        "/api/exam/start",
        json={"subject": "m1", "question_count": 6},
        headers=headers,
    ).json()["attempt_id"]

    cuerpo = client.post(
        f"/api/exam/{aid}/salida", json={"segundos": 8 * 3600}, headers=headers
    ).json()

    assert cuerpo["segundos_fuera"] == service.MAX_SEGUNDOS_POR_SALIDA


def test_volver_a_un_ensayo_entregado_no_cuenta_como_salida(
    db_session: Session, register_user
) -> None:
    """Abrir la pestaña de un ensayo ya terminado no es salirse de nada."""
    _, user = register_user(email="terminado@milpaes.cl")
    attempt = ExamAttempt(
        user_id=user["id"], subject=Subject.M1, status=AttemptStatus.SUBMITTED
    )
    db_session.add(attempt)
    db_session.commit()

    service.registrar_salida(db_session, attempt, 60)

    assert attempt.salidas == 0
    assert attempt.segundos_fuera == 0
