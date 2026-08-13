from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from paes_api.modules.content.models import Alternative, Difficulty, Question
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode


def _make_node_with_question(db_session: Session, code: str) -> tuple[SkillNode, Question, Alternative, Alternative]:
    node = SkillNode(
        code=code, name=code, axis=SkillAxis.NUMEROS, tier=1, unlock_threshold=0.75
    )
    db_session.add(node)
    db_session.flush()

    question = Question(
        skill_node_id=node.id, difficulty=Difficulty.FACIL, stem="¿Cuánto es 2 + 2?"
    )
    db_session.add(question)
    db_session.flush()

    correct = Alternative(question_id=question.id, label="A", text="4", is_correct=True)
    wrong = Alternative(question_id=question.id, label="B", text="5", is_correct=False)
    db_session.add_all([correct, wrong])
    db_session.commit()
    db_session.refresh(question)
    return node, question, correct, wrong


def test_practice_questions_403_when_node_locked(
    client: TestClient, db_session: Session, register_user
) -> None:
    locked = SkillNode(code="bloqueado", name="Bloqueado", axis=SkillAxis.NUMEROS, tier=2)
    prereq = SkillNode(code="previo", name="Previo", axis=SkillAxis.NUMEROS, tier=1)
    locked.prerequisites = [prereq]
    db_session.add_all([prereq, locked])
    db_session.commit()

    headers, _ = register_user(email="practica-bloqueada@milpaes.cl")
    resp = client.get("/api/practice/bloqueado/questions", headers=headers)
    assert resp.status_code == 403


def test_practice_questions_404_for_unknown_node(
    client: TestClient, register_user
) -> None:
    headers, _ = register_user(email="practica-404@milpaes.cl")
    resp = client.get("/api/practice/no-existe/questions", headers=headers)
    assert resp.status_code == 404


def test_practice_answer_correct_updates_progress(
    client: TestClient, db_session: Session, register_user
) -> None:
    _node, question, correct, _wrong = _make_node_with_question(db_session, "suma")
    headers, _ = register_user(email="practica-ok@milpaes.cl")

    start = client.get("/api/practice/suma/questions", headers=headers)
    assert start.status_code == 200
    assert start.json()["questions"][0]["id"] == question.id

    resp = client.post(
        "/api/practice/suma/answer",
        json={"question_id": question.id, "selected_alternative_id": correct.id},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_correct"] is True
    assert body["correct_alternative_id"] == correct.id
    assert body["node_attempts"] == 1
    assert body["node_accuracy"] == 1.0


def test_practice_answer_unlocks_dependent_node(
    client: TestClient, db_session: Session, register_user
) -> None:
    node, question, correct, _wrong = _make_node_with_question(db_session, "raiz_practica")
    child = SkillNode(
        code="hijo_practica",
        name="Hijo",
        axis=SkillAxis.NUMEROS,
        tier=2,
        unlock_threshold=0.75,
        prerequisites=[node],
    )
    db_session.add(child)
    db_session.commit()

    headers, _ = register_user(email="practica-unlock@milpaes.cl")

    for _ in range(4):
        resp = client.post(
            "/api/practice/raiz_practica/answer",
            json={"question_id": question.id, "selected_alternative_id": correct.id},
            headers=headers,
        )
        assert resp.status_code == 200

    assert resp.json()["newly_unlocked"] == ["Hijo"]


def test_practice_answer_invalid_alternative_is_422(
    client: TestClient, db_session: Session, register_user
) -> None:
    _node, question, _correct, _wrong = _make_node_with_question(db_session, "invalido")
    headers, _ = register_user(email="practica-422@milpaes.cl")

    resp = client.post(
        "/api/practice/invalido/answer",
        json={"question_id": question.id, "selected_alternative_id": 999_999},
        headers=headers,
    )
    assert resp.status_code == 422
