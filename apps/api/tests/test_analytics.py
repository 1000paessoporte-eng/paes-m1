from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from test_practice import _make_node_with_question


def test_summary_counts_practice_answers(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Antes del fix, /api/analytics/summary solo miraba ExamAnswer: un
    usuario que solo practica (nunca rinde un ensayo) aparecía sin ninguna
    actividad, sin racha y sin preguntas respondidas."""
    _node, question, correct, wrong = _make_node_with_question(db_session, "raiz_analitica")
    headers, _ = register_user(email="analitica-practica@milpaes.cl")

    client.post(
        "/api/practice/raiz_analitica/answer",
        json={"question_id": question.id, "selected_alternative_id": correct.id},
        headers=headers,
    )
    client.post(
        "/api/practice/raiz_analitica/answer",
        json={"question_id": question.id, "selected_alternative_id": wrong.id},
        headers=headers,
    )

    resp = client.get("/api/analytics/summary", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_questions_answered"] == 2
    assert body["total_correct"] == 1
    assert body["overall_accuracy"] == 0.5
    assert body["current_streak_days"] == 1
    # La practica no mide tiempo por pregunta (a diferencia del ensayo), asi
    # que no debe inventar minutos practicados.
    assert body["total_minutes_practiced"] == 0.0
