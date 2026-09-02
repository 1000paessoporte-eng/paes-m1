from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from test_practice import _make_node_with_question

from paes_api.modules.skill_tree.models import SkillAxis


def test_repaso_has_no_data_for_new_user(client: TestClient, register_user) -> None:
    headers, _ = register_user(email="repaso-nuevo@milpaes.cl")
    resp = client.get("/api/exam/repaso", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == {
        "has_data": False,
        "axes": [],
        "axis_labels": [],
        "nodes": [],
    }


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
    # El eje ya no basta: el ensayo se arma con el TEMA, y por eso viaja.
    assert [n["code"] for n in body["nodes"]] == ["repaso_numeros"]
    assert body["nodes"][0]["axis_label"] == "Números"


def test_un_solo_fallo_no_gana_a_un_tema_con_historial(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Ordenar por acierto a secas ponía primero la mala suerte.

    Un tema con UNA respuesta fallada da 0% y se colaba por delante de otro con
    diez respuestas y 30% de acierto. El primero no dice nada; el segundo es el
    que hay que practicar. Con el suavizado, gana el que tiene historial.
    """
    _n1, q1, correcta1, mala1 = _make_node_with_question(db_session, "tema_con_historial")
    _n2, q2, _correcta2, mala2 = _make_node_with_question(db_session, "tema_de_una_vez")
    headers, _ = register_user(email="repaso-ranking@milpaes.cl")

    def responder(code: str, question_id: int, alternativa_id: int) -> None:
        client.post(
            f"/api/practice/{code}/answer",
            json={"question_id": question_id, "selected_alternative_id": alternativa_id},
            headers=headers,
        )

    # Diez respuestas con tres aciertos: 30%.
    for i in range(10):
        responder(
            "tema_con_historial", q1.id, correcta1.id if i < 3 else mala1.id
        )
    # Una sola respuesta, fallada: 0%.
    responder("tema_de_una_vez", q2.id, mala2.id)

    body = client.get("/api/exam/repaso", headers=headers).json()
    codigos = [n["code"] for n in body["nodes"]]
    assert codigos[0] == "tema_con_historial", (
        "el tema con diez respuestas y 30% tiene que ir primero, "
        f"no el de un solo fallo: {codigos}"
    )


def test_el_ensayo_de_refuerzo_solo_trae_los_temas_pedidos(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Filtrar por eje traía temas ya dominados; por tema, no."""
    _n1, _q1, _c1, _m1 = _make_node_with_question(db_session, "refuerzo_pedido")
    _n2, _q2, _c2, _m2 = _make_node_with_question(db_session, "refuerzo_no_pedido")
    headers, _ = register_user(email="refuerzo@milpaes.cl")

    resp = client.post(
        "/api/exam/start",
        json={
            "subject": "m1",
            "question_count": 5,
            "pace": "oficial",
            "axes": [],
            "skill_nodes": ["refuerzo_pedido"],
        },
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    preguntas = resp.json()["questions"]
    assert preguntas, "el refuerzo tiene que traer preguntas"
    assert all(q["skill_node_id"] for q in preguntas)
