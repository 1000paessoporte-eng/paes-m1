"""Repaso inteligente: la pregunta fallada vuelve hasta que la domina.

Lo que fijan estos tests es lo que hace que el repaso sirva o estorbe: que solo
entren las que sigue fallando, que acertar la aleje y fallar la devuelva, y que
repasar cuente como estudiar.
"""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from paes_api.modules.content.models import Alternative, Difficulty, Question
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.repaso import service
from paes_api.modules.repaso.models import RepasoItem
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode


@pytest.fixture()
def pregunta(db_session: Session) -> Question:
    """Una pregunta del banco con su correcta y su distractor."""
    node = SkillNode(
        code="nodo_repaso", name="Tema de prueba", axis=SkillAxis.NUMEROS, tier=1,
        unlock_threshold=0.75,
    )
    db_session.add(node)
    db_session.flush()
    q = Question(
        skill_node_id=node.id, difficulty=Difficulty.MEDIO, stem="¿Cuánto es 2 + 2?",
        explanation="Se suman.",
    )
    db_session.add(q)
    db_session.flush()
    db_session.add_all(
        [
            Alternative(question_id=q.id, label="A", text="4", is_correct=True),
            Alternative(
                question_id=q.id, label="B", text="22", is_correct=False,
                distractor_justification="Concatenó los dígitos en vez de sumarlos.",
            ),
        ]
    )
    db_session.commit()
    return q


def _fallar(db: Session, user_id: int, q: Question, cuando: datetime | None = None) -> None:
    db.add(
        PracticeAnswer(
            user_id=user_id, question_id=q.id, skill_node_id=q.skill_node_id,
            is_correct=False, answered_at=cuando or datetime.now(UTC),
        )
    )
    db.commit()


def _acertar(db: Session, user_id: int, q: Question, cuando: datetime) -> None:
    db.add(
        PracticeAnswer(
            user_id=user_id, question_id=q.id, skill_node_id=q.skill_node_id,
            is_correct=True, answered_at=cuando,
        )
    )
    db.commit()


def test_la_fallada_entra_a_la_cola(
    client: TestClient, register_user, db_session: Session, pregunta: Question
) -> None:
    headers, user = register_user()
    _fallar(db_session, user["id"], pregunta)

    body = client.get("/api/repaso/resumen", headers=headers).json()
    assert body["pendientes_hoy"] == 1
    assert body["dominadas"] == 0


def test_la_que_despues_acerto_no_entra(
    client: TestClient, register_user, db_session: Session, pregunta: Question
) -> None:
    """Falló en marzo y acertó en mayo: ya no es material de repaso, y
    arrastrarla gastaría la sesión en algo que resolvió solo."""
    headers, user = register_user()
    ayer = datetime.now(UTC) - timedelta(days=1)
    _fallar(db_session, user["id"], pregunta, cuando=ayer)
    _acertar(db_session, user["id"], pregunta, cuando=datetime.now(UTC))

    assert client.get("/api/repaso/resumen", headers=headers).json()["pendientes_hoy"] == 0


def test_la_cola_no_duplica_la_misma_pregunta(
    client: TestClient, register_user, db_session: Session, pregunta: Question
) -> None:
    """Fallarla dos veces no la programa dos veces: dentro de una sesión se
    vería repetida."""
    headers, user = register_user()
    _fallar(db_session, user["id"], pregunta)
    _fallar(db_session, user["id"], pregunta)

    client.get("/api/repaso/resumen", headers=headers)
    client.get("/api/repaso/resumen", headers=headers)

    items = db_session.query(RepasoItem).filter_by(user_id=user["id"]).all()
    assert len(items) == 1


def test_acertar_la_aleja_y_fallar_la_devuelve_maniana(
    client: TestClient, register_user, db_session: Session, pregunta: Question
) -> None:
    headers, user = register_user()
    _fallar(db_session, user["id"], pregunta)
    client.get("/api/repaso/sesion", headers=headers)

    correcta = next(a for a in pregunta.alternatives if a.is_correct)
    incorrecta = next(a for a in pregunta.alternatives if not a.is_correct)

    resp = client.post(
        "/api/repaso/responder",
        headers=headers,
        json={"question_id": pregunta.id, "selected_alternative_id": correcta.id},
    ).json()
    assert resp["is_correct"] is True
    # Sube al peldaño 1: el intervalo que le toca es el de ESE peldaño.
    assert resp["nivel"] == 1
    assert resp["proxima_fecha"] == str(datetime.now(UTC).date() + timedelta(days=service.ESCALERA_DIAS[1]))

    resp = client.post(
        "/api/repaso/responder",
        headers=headers,
        json={"question_id": pregunta.id, "selected_alternative_id": incorrecta.id},
    ).json()
    assert resp["is_correct"] is False
    assert resp["nivel"] == 0
    # Mañana, no hoy: en la misma sesión la recordaría de memoria.
    assert resp["proxima_fecha"] == str(datetime.now(UTC).date() + timedelta(days=1))
    assert "Concatenó" in resp["distractor_justification"]


def test_acertarla_toda_la_escalera_la_saca_de_la_cola(
    client: TestClient, register_user, db_session: Session, pregunta: Question
) -> None:
    headers, user = register_user()
    _fallar(db_session, user["id"], pregunta)
    client.get("/api/repaso/resumen", headers=headers)

    item = db_session.query(RepasoItem).filter_by(user_id=user["id"]).one()
    for _ in range(len(service.ESCALERA_DIAS)):
        service.registrar_respuesta(item, acerto=True)
    db_session.commit()

    assert item.proxima_fecha is None
    assert item.dominada is True
    body = client.get("/api/repaso/resumen", headers=headers).json()
    assert body["dominadas"] == 1
    assert body["pendientes_hoy"] == 0


def test_repasar_cuenta_como_estudiar(
    client: TestClient, register_user, db_session: Session, pregunta: Question
) -> None:
    """Sin esto, quien estudia repasando aparecería en la analítica como que no
    estudió, y la racha que le pedimos sostener no se movería."""
    headers, user = register_user()
    _fallar(db_session, user["id"], pregunta)
    client.get("/api/repaso/sesion", headers=headers)
    antes = db_session.query(PracticeAnswer).filter_by(user_id=user["id"]).count()

    correcta = next(a for a in pregunta.alternatives if a.is_correct)
    client.post(
        "/api/repaso/responder",
        headers=headers,
        json={"question_id": pregunta.id, "selected_alternative_id": correcta.id},
    )

    assert db_session.query(PracticeAnswer).filter_by(user_id=user["id"]).count() == antes + 1


def test_no_se_puede_responder_algo_ajeno_al_repaso(
    client: TestClient, register_user, pregunta: Question
) -> None:
    headers, _ = register_user()
    correcta = next(a for a in pregunta.alternatives if a.is_correct)
    resp = client.post(
        "/api/repaso/responder",
        headers=headers,
        json={"question_id": pregunta.id, "selected_alternative_id": correcta.id},
    )
    assert resp.status_code == 404


def test_la_sesion_se_corta_en_el_limite(
    client: TestClient, register_user, db_session: Session
) -> None:
    """Una cola de noventa no se empieza: se cierra."""
    headers, user = register_user()
    node = SkillNode(
        code="nodo_masivo", name="Tema", axis=SkillAxis.ALGEBRA, tier=1, unlock_threshold=0.75
    )
    db_session.add(node)
    db_session.flush()
    for i in range(service.LIMITE_SESION + 5):
        q = Question(skill_node_id=node.id, difficulty=Difficulty.FACIL, stem=f"Pregunta {i}")
        db_session.add(q)
        db_session.flush()
        db_session.add(Alternative(question_id=q.id, label="A", text="x", is_correct=True))
        db_session.add(
            PracticeAnswer(
                user_id=user["id"], question_id=q.id, skill_node_id=node.id, is_correct=False
            )
        )
    db_session.commit()

    body = client.get("/api/repaso/sesion", headers=headers).json()
    assert len(body["preguntas"]) == service.LIMITE_SESION
    assert body["pendientes_totales"] == service.LIMITE_SESION + 5


def test_la_pregunta_de_lectora_trae_su_texto(
    client: TestClient, register_user, db_session: Session
) -> None:
    """En Competencia Lectora la respuesta está EN el texto: servir la pregunta
    sin él la vuelve imposible de responder.

    Este test existe porque el router leía `passage.content` y el campo se
    llama `body`: cualquier alumno con una pregunta de Lectora fallada recibía
    un 500 en toda la sesión, no solo en esa pregunta.
    """
    from paes_api.modules.content.models import ReadingPassage

    headers, user = register_user()
    node = SkillNode(
        code="nodo_lectora", name="Localizar", axis=SkillAxis.NUMEROS, tier=1,
        unlock_threshold=0.75,
    )
    db_session.add(node)
    db_session.flush()
    texto = ReadingPassage(title="El faro", body="Un texto de prueba con dos líneas.")
    db_session.add(texto)
    db_session.flush()
    q = Question(
        skill_node_id=node.id, difficulty=Difficulty.MEDIO,
        stem="¿Qué dice el texto?", passage_id=texto.id,
    )
    db_session.add(q)
    db_session.flush()
    db_session.add(Alternative(question_id=q.id, label="A", text="Algo", is_correct=True))
    db_session.commit()
    _fallar(db_session, user["id"], q)

    resp = client.get("/api/repaso/sesion", headers=headers)
    assert resp.status_code == 200, resp.text
    pregunta = resp.json()["preguntas"][0]
    assert pregunta["passage"] == "Un texto de prueba con dos líneas."
    assert pregunta["passage_title"] == "El faro"
