from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from paes_api.modules.content.models import (
    Alternative,
    Difficulty,
    Question,
    ReadingPassage,
)
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode, Subject


def _make_node_with_question(db_session: Session, code: str) -> tuple[Question, Alternative, Alternative]:
    node = SkillNode(
        code=code, name=code, axis=SkillAxis.NUMEROS, tier=1, unlock_threshold=0.75
    )
    db_session.add(node)
    db_session.flush()

    question = Question(
        skill_node_id=node.id,
        difficulty=Difficulty.FACIL,
        stem="¿Cuánto es 2 + 2?",
        explanation="2+2=4.",
    )
    db_session.add(question)
    db_session.flush()

    correct = Alternative(question_id=question.id, label="A", text="4", is_correct=True)
    wrong = Alternative(question_id=question.id, label="B", text="5", is_correct=False)
    db_session.add_all([correct, wrong])
    db_session.commit()
    db_session.refresh(question)
    return question, correct, wrong


def test_demo_questions_no_auth_required_and_hides_correct_answer(
    client: TestClient, db_session: Session
) -> None:
    _make_node_with_question(db_session, "demo_node")

    resp = client.get("/api/demo/questions")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) >= 1
    for question in body:
        for alt in question["alternatives"]:
            assert "is_correct" not in alt


def test_demo_grade_scores_without_persisting_anything(
    client: TestClient, db_session: Session
) -> None:
    question, correct, wrong = _make_node_with_question(db_session, "demo_node2")

    resp = client.post(
        "/api/demo/grade",
        json={"answers": [{"question_id": question.id, "selected_alternative_id": correct.id}]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["correct"] == 1
    assert body["total"] == 1
    assert body["items"][0]["is_correct"] is True
    assert body["items"][0]["correct_alternative_id"] == correct.id
    assert body["items"][0]["explanation"] == "2+2=4."

    resp_wrong = client.post(
        "/api/demo/grade",
        json={"answers": [{"question_id": question.id, "selected_alternative_id": wrong.id}]},
    )
    assert resp_wrong.json()["correct"] == 0


def test_demo_questions_solo_de_la_prueba_pedida(
    client: TestClient, db_session: Session
) -> None:
    """Antes el sorteo salía de todo el banco: quien probaba M1 podía recibir
    una pregunta de Historia con el rótulo de matemática encima."""
    _make_node_with_question(db_session, "demo_m1")
    nodo_historia = SkillNode(
        code="demo_hist",
        name="Demo Historia",
        axis=SkillAxis.HISTORIA,
        subject=Subject.HISTORIA,
        tier=1,
        unlock_threshold=0.75,
    )
    db_session.add(nodo_historia)
    db_session.flush()
    db_session.add(
        Question(
            skill_node_id=nodo_historia.id,
            difficulty=Difficulty.FACIL,
            stem="¿En qué año fue la independencia?",
        )
    )
    db_session.commit()

    m1 = client.get("/api/demo/questions").json()
    assert m1, "la demo por defecto debe traer preguntas de M1"
    assert all(q["subject"] == "m1" for q in m1)

    historia = client.get("/api/demo/questions", params={"subject": "historia"}).json()
    assert [q["subject"] for q in historia] == ["historia"]


def test_demo_lectora_viaja_con_su_texto(client: TestClient, db_session: Session) -> None:
    """Una pregunta de lectora sin su pasaje es incontestable: la demo la
    mostraba igual porque el pasaje no viajaba en la respuesta."""
    pasaje = ReadingPassage(title="Texto de prueba", body="Cuerpo del texto.", kind="no_literario")
    nodo = SkillNode(
        code="demo_lectora",
        name="Localizar información",
        axis=SkillAxis.LOCALIZAR,
        subject=Subject.LECTORA,
        tier=1,
        unlock_threshold=0.75,
    )
    db_session.add_all([pasaje, nodo])
    db_session.flush()
    db_session.add(
        Question(
            skill_node_id=nodo.id,
            difficulty=Difficulty.FACIL,
            stem="¿Qué dice el texto?",
            passage_id=pasaje.id,
        )
    )
    db_session.commit()

    body = client.get("/api/demo/questions", params={"subject": "lectora"}).json()
    assert body[0]["passage"]["title"] == "Texto de prueba"
    assert body[0]["node_name"] == "Localizar información"
    assert body[0]["axis"] == "localizar"
