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
    # Toda alternativa incorrecta lleva su justificación: es el contrato del
    # modelo (ver Alternative en content/models.py) y lo que la demo devuelve
    # a quien falla.
    wrong = Alternative(
        question_id=question.id,
        label="B",
        text="5",
        is_correct=False,
        distractor_justification="Contó uno de más al sumar.",
    )
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


def test_demo_grade_devuelve_la_justificacion_del_distractor_elegido(
    client: TestClient, db_session: Session
) -> None:
    """Quien falla tiene que ver POR QUÉ falló, no solo la resolución.

    Es lo que promete la portada ("el razonamiento exacto que te llevó a la
    alternativa incorrecta"). La demo tenía la justificación escrita en la base
    para todas las alternativas incorrectas del banco y no la devolvía: quien
    probaba sin cuenta recibía la explicación genérica y se iba sin ver lo
    único que distingue esto de un PDF de ejercicios.
    """
    question, correct, wrong = _make_node_with_question(db_session, "demo_distractor")

    fallada = client.post(
        "/api/demo/grade",
        json={"answers": [{"question_id": question.id, "selected_alternative_id": wrong.id}]},
    ).json()["items"][0]
    assert fallada["is_correct"] is False
    assert fallada["selected_alternative_id"] == wrong.id
    assert fallada["distractor_justification"] == "Contó uno de más al sumar."

    # Al acertar no hay distractor que justificar.
    acertada = client.post(
        "/api/demo/grade",
        json={"answers": [{"question_id": question.id, "selected_alternative_id": correct.id}]},
    ).json()["items"][0]
    assert acertada["distractor_justification"] is None

    # Sin responder tampoco: no se marcó ninguna alternativa.
    en_blanco = client.post(
        "/api/demo/grade",
        json={"answers": [{"question_id": question.id, "selected_alternative_id": None}]},
    ).json()["items"][0]
    assert en_blanco["is_correct"] is False
    assert en_blanco["distractor_justification"] is None


def test_demo_grade_no_filtra_las_justificaciones_no_elegidas(
    client: TestClient, db_session: Session
) -> None:
    """Solo viaja la justificación de la alternativa marcada.

    Devolverlas todas le regalaría al estudiante el descarte de las otras tres
    antes de haber pensado, que es justo lo que el ensayo no debe hacer.
    """
    question, _correct, wrong = _make_node_with_question(db_session, "demo_no_filtra")

    cuerpo = client.post(
        "/api/demo/grade",
        json={"answers": [{"question_id": question.id, "selected_alternative_id": wrong.id}]},
    ).text
    assert "Contó uno de más al sumar." in cuerpo
    assert cuerpo.count("distractor_justification") == 1


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


def test_demo_pregunta_con_figura_viaja_con_su_figura(
    client: TestClient, db_session: Session
) -> None:
    """Una pregunta que habla de "la figura" es incontestable sin ella.

    El ensayo, la práctica y la revisión ya la entregaban; la demo no, porque
    se escribió cuando ninguna pregunta de M1 tenía figura. Desde que M1, M2 e
    Historia las tienen, la demo pública podía mostrar un enunciado que se
    refiere a un dibujo que nunca llega.
    """
    nodo = SkillNode(
        code="demo_geometria",
        name="Perímetros y áreas",
        axis=SkillAxis.GEOMETRIA,
        subject=Subject.M1,
        tier=1,
        unlock_threshold=0.75,
    )
    db_session.add(nodo)
    db_session.flush()
    db_session.add(
        Question(
            skill_node_id=nodo.id,
            difficulty=Difficulty.FACIL,
            stem="¿Cuál es el área del trapecio de la figura?",
            image_url="/preguntas/mat-trapecio-acotado.svg",
        )
    )
    db_session.commit()

    body = client.get("/api/demo/questions", params={"subject": "m1"}).json()
    assert body[0]["image_url"] == "/preguntas/mat-trapecio-acotado.svg"
