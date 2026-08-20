from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from test_practice import _make_node_with_question


def test_uso_publico_arranca_en_cero_y_no_pide_sesion(client: TestClient) -> None:
    """Es el dato que la portada usa como prueba social: tiene que poder
    leerse sin cuenta, y con la base vacía tiene que decir cero en vez de
    fallar."""
    resp = client.get("/api/metrics/uso")
    assert resp.status_code == 200
    assert resp.json() == {
        "ensayos_rendidos": 0,
        "preguntas_respondidas": 0,
        "alumnos": 0,
    }


def test_uso_publico_cuenta_la_practica_y_no_los_ensayos_a_medias(
    client: TestClient, db_session: Session, register_user
) -> None:
    _node, question, correct, _wrong = _make_node_with_question(db_session, "raiz_uso")
    headers, _ = register_user(email="uso@milpaes.cl")

    client.post(
        "/api/practice/raiz_uso/answer",
        json={"question_id": question.id, "selected_alternative_id": correct.id},
        headers=headers,
    )
    # Un ensayo abierto y nunca entregado no es un ensayo rendido.
    client.post("/api/exam/start", json={"subject": "m1"}, headers=headers)

    body = client.get("/api/metrics/uso").json()
    assert body["preguntas_respondidas"] == 1
    assert body["ensayos_rendidos"] == 0
    assert body["alumnos"] == 0
