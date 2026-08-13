from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from test_practice import _make_node_with_question

from paes_api.modules.skill_tree.models import SkillAxis


def test_repaso_has_no_data_for_new_user(client: TestClient, register_user) -> None:
    headers, _ = register_user(email="repaso-nuevo@milpaes.cl")
    resp = client.get("/api/exam/repaso", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == {"has_data": False, "axes": [], "axis_labels": []}


def test_repaso_suggests_axis_of_weakest_attempted_node(
    client: TestClient, db_session: Session, register_user
) -> None:
    _node, question, _correct, wrong = _make_node_with_question(db_session, "repaso_numeros")
    headers, _ = register_user(email="repaso-debil@milpaes.cl")

    client.post(
        "/api/practice/repaso_numeros/answer",
        json={"question_id": question.id, "selected_alternative_id": wrong.id},
        headers=headers,
    )

    resp = client.get("/api/exam/repaso", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["has_data"] is True
    assert body["axes"] == [SkillAxis.NUMEROS.value]
    assert body["axis_labels"] == ["Números"]
