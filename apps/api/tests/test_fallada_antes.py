"""La marca "esta pregunta ya la fallaste", dentro del ensayo.

Reemplaza al módulo de repaso: en vez de una cola aparte a la que hay que
entrar, la señal aparece donde sirve, con la pregunta al frente.
"""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.content.models import Alternative, Difficulty, Question
from paes_api.modules.exam_focus.service import preguntas_falladas_antes
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode
from paes_api.modules.users.models import User


def _pregunta(db: Session, node: SkillNode, stem: str) -> Question:
    q = Question(skill_node_id=node.id, difficulty=Difficulty.MEDIO, stem=stem)
    db.add(q)
    db.flush()
    db.add_all(
        [
            Alternative(question_id=q.id, label="A", text="ok", is_correct=True),
            Alternative(question_id=q.id, label="B", text="mal", is_correct=False),
        ]
    )
    db.commit()
    return q


def _nodo(db: Session, code: str) -> SkillNode:
    n = SkillNode(
        code=code, name="Tema", axis=SkillAxis.NUMEROS, tier=1, unlock_threshold=0.75
    )
    db.add(n)
    db.flush()
    db.commit()
    return n


def test_marca_la_que_fallo_practicando(db_session: Session) -> None:
    node = _nodo(db_session, "n_fall")
    fallada = _pregunta(db_session, node, "La que falló")
    acertada = _pregunta(db_session, node, "La que acertó")
    user = User(email="marca@milpaes.cl", name="Marca", hashed_password="x")
    db_session.add(user)
    db_session.flush()
    db_session.add_all(
        [
            PracticeAnswer(
                user_id=user.id, question_id=fallada.id,
                skill_node_id=node.id, is_correct=False,
            ),
            PracticeAnswer(
                user_id=user.id, question_id=acertada.id,
                skill_node_id=node.id, is_correct=True,
            ),
        ]
    )
    db_session.commit()

    marcadas = preguntas_falladas_antes(
        db_session, user.id, [fallada.id, acertada.id], excluir_intento=0
    )
    assert marcadas == {fallada.id}


def _banco(db: Session, code: str, cuantas: int) -> list[Question]:
    """Un nodo de M1 con preguntas suficientes para armar un ensayo."""
    node = _nodo(db, code)
    return [_pregunta(db, node, f"Pregunta {i}") for i in range(cuantas)]


def test_no_marca_lo_del_intento_en_curso(
    client: TestClient, register_user, db_session: Session
) -> None:
    """Dentro del mismo ensayo la pregunta se responde una sola vez: marcarla
    con lo que el alumno acaba de contestar sería decirle la respuesta."""
    _banco(db_session, "n_curso", 5)
    headers, _ = register_user()

    cuerpo = client.post(
        "/api/exam/start",
        headers=headers,
        json={"subject": "m1", "pace": "oficial", "question_count": 5, "axes": []},
    ).json()
    attempt_id = cuerpo["attempt_id"]
    pregunta = cuerpo["questions"][0]

    mala = db_session.execute(
        select(Alternative).where(
            Alternative.question_id == pregunta["id"],
            Alternative.is_correct.is_(False),
        )
    ).scalars().first()

    client.post(
        f"/api/exam/{attempt_id}/answer",
        headers=headers,
        json={
            "question_id": pregunta["id"],
            "selected_alternative_id": mala.id,
            "time_spent_ms": 1000,
        },
    )

    estado = client.get(f"/api/exam/{attempt_id}", headers=headers).json()
    esta = next(q for q in estado["questions"] if q["id"] == pregunta["id"])
    assert esta["fallada_antes"] is False


def test_la_marca_aparece_en_el_ensayo_siguiente(
    client: TestClient, register_user, db_session: Session
) -> None:
    """Lo que se falló en un ensayo se avisa en el siguiente, que es todo el
    punto de la función."""
    _banco(db_session, "n_siguiente", 4)
    headers, _ = register_user()

    primero = client.post(
        "/api/exam/start",
        headers=headers,
        json={"subject": "m1", "pace": "oficial", "question_count": 4, "axes": []},
    ).json()
    fallada_id = primero["questions"][0]["id"]
    mala = db_session.execute(
        select(Alternative).where(
            Alternative.question_id == fallada_id, Alternative.is_correct.is_(False)
        )
    ).scalars().first()
    client.post(
        f"/api/exam/{primero['attempt_id']}/answer",
        headers=headers,
        json={
            "question_id": fallada_id,
            "selected_alternative_id": mala.id,
            "time_spent_ms": 1000,
        },
    )
    client.post(f"/api/exam/{primero['attempt_id']}/submit", headers=headers)

    segundo = client.post(
        "/api/exam/start",
        headers=headers,
        json={"subject": "m1", "pace": "oficial", "question_count": 4, "axes": []},
    ).json()
    marcada = next(q for q in segundo["questions"] if q["id"] == fallada_id)
    assert marcada["fallada_antes"] is True
    # Las demás no se marcan solo por haber aparecido antes.
    otras = [q for q in segundo["questions"] if q["id"] != fallada_id]
    assert all(q["fallada_antes"] is False for q in otras)


def test_el_ensayo_entrega_la_marca(
    client: TestClient, register_user, db_session: Session
) -> None:
    """El campo viaja siempre, aunque nadie haya fallado nada todavía."""
    _banco(db_session, "n_marca", 3)
    headers, _ = register_user()
    cuerpo = client.post(
        "/api/exam/start",
        headers=headers,
        json={"subject": "m1", "pace": "oficial", "question_count": 3, "axes": []},
    ).json()
    assert all("fallada_antes" in q for q in cuerpo["questions"])
    assert all(q["fallada_antes"] is False for q in cuerpo["questions"])
