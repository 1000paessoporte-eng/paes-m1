"""El botón de reportar una pregunta mal planteada.

El banco lo escribimos nosotros y tiene miles de preguntas. `verificar_banco.py`
recalcula la aritmética y comprueba la estructura, pero no ve un enunciado
ambiguo ni una clave apuntando a la alternativa equivocada. Eso lo ve quien
responde, y hasta ahora no tenía dónde decirlo.
"""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from test_practice import _make_node_with_question

from paes_api.modules.reportes.models import ReportePregunta
from paes_api.modules.users.models import User


def _hacer_admin(db: Session, email: str) -> None:
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    user.is_admin = True
    db.commit()


def test_se_reporta_sin_sesion(client: TestClient, db_session: Session) -> None:
    """La demo se responde sin cuenta, y es donde entra gente que nunca nos va
    a escribir un correo."""
    _node, question, _c, _w = _make_node_with_question(db_session, "raiz_rep_anon")

    resp = client.post(
        "/api/reportes",
        json={
            "question_id": question.id,
            "motivo": "respuesta_incorrecta",
            "contexto": "revision",
        },
    )
    assert resp.status_code == 204, resp.text

    fila = db_session.execute(select(ReportePregunta)).scalars().one()
    assert fila.user_id is None
    assert fila.comentario is None
    assert fila.revisado_en is None


def test_el_comentario_es_opcional_pero_se_guarda(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Pedir un texto obligatorio en el minuto 80 de un ensayo es pedir que
    nadie reporte. Pero cuando lo escriben, es el dato que decide."""
    _node, question, _c, _w = _make_node_with_question(db_session, "raiz_rep_coment")
    headers, _ = register_user(email="reporta@milpaes.cl")

    client.post(
        "/api/reportes",
        json={
            "question_id": question.id,
            "motivo": "varias_correctas",
            "comentario": "  La B también es correcta si el número es negativo  ",
            "contexto": "ensayo",
        },
        headers=headers,
    )

    fila = db_session.execute(select(ReportePregunta)).scalars().one()
    assert fila.comentario == "La B también es correcta si el número es negativo"
    assert fila.contexto == "ensayo"
    assert fila.user_id is not None


def test_el_mismo_alumno_dos_veces_es_un_solo_aviso(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Se reporta durante el ensayo y otra vez en la retroalimentación, al ver
    que la clave era la que uno había descartado. Es un aviso, no dos: si
    contara doble, inflaría justo el número con que priorizamos."""
    _node, question, _c, _w = _make_node_with_question(db_session, "raiz_rep_doble")
    headers, _ = register_user(email="insiste@milpaes.cl")
    cuerpo = {
        "question_id": question.id,
        "motivo": "enunciado_confuso",
        "contexto": "ensayo",
    }

    client.post("/api/reportes", json=cuerpo, headers=headers)
    client.post("/api/reportes", json={**cuerpo, "contexto": "revision"}, headers=headers)

    assert len(db_session.execute(select(ReportePregunta)).scalars().all()) == 1


def test_una_pregunta_que_no_existe_no_se_reporta(client: TestClient) -> None:
    """El endpoint es público: no puede servir para escribir filas sueltas
    apuntando a nada."""
    resp = client.post(
        "/api/reportes",
        json={"question_id": 999999, "motivo": "otro", "contexto": "practica"},
    )
    assert resp.status_code == 404


def test_el_panel_es_solo_de_admin(
    client: TestClient, db_session: Session, register_user
) -> None:
    headers, _ = register_user(email="curiosa@milpaes.cl")
    assert client.get("/api/reportes").status_code == 401
    assert client.get("/api/reportes", headers=headers).status_code == 404


def test_el_panel_agrupa_por_pregunta_y_ordena_por_cuanta_gente_aviso(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Lo que se arregla es la pregunta, y el orden en que hay que mirarlas lo
    da cuánta gente avisó."""
    _n1, tranquila, _c, _w = _make_node_with_question(db_session, "raiz_rep_una")
    _n2, sospechosa, correcta, _w2 = _make_node_with_question(db_session, "raiz_rep_dos")

    for i in range(3):
        headers, _ = register_user(email=f"avisa{i}@milpaes.cl")
        client.post(
            "/api/reportes",
            json={
                "question_id": sospechosa.id,
                "motivo": "respuesta_incorrecta",
                "contexto": "revision",
            },
            headers=headers,
        )
    client.post(
        "/api/reportes",
        json={"question_id": tranquila.id, "motivo": "otro", "contexto": "practica"},
    )

    admin_headers, _ = register_user(email="jefa@milpaes.cl")
    _hacer_admin(db_session, "jefa@milpaes.cl")
    cuerpo = client.get("/api/reportes", headers=admin_headers).json()

    assert [r["question_id"] for r in cuerpo] == [sospechosa.id, tranquila.id]
    assert cuerpo[0]["reportes"] == 3
    assert cuerpo[0]["pendientes"] == 3
    assert cuerpo[0]["motivos"] == {"respuesta_incorrecta": 3}
    # El panel tiene que poder decidir sin salir de ahí: enunciado, nodo y la
    # alternativa que el banco da por correcta.
    assert cuerpo[0]["stem"] == sospechosa.stem
    assert cuerpo[0]["respuesta_correcta"] == correcta.text
    assert cuerpo[0]["skill_node_name"] == "raiz_rep_dos"


def test_marcar_revisado_saca_la_pregunta_del_panel(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Vale igual si la pregunta se corrigió o si se revisó y estaba bien: en
    los dos casos ya no hay nada que hacer con esos avisos."""
    _node, question, _c, _w = _make_node_with_question(db_session, "raiz_rep_cerrar")
    client.post(
        "/api/reportes",
        json={"question_id": question.id, "motivo": "datos_erroneos", "contexto": "ensayo"},
    )

    headers, _ = register_user(email="cierra@milpaes.cl")
    _hacer_admin(db_session, "cierra@milpaes.cl")

    assert client.post(f"/api/reportes/{question.id}/revisado", headers=headers).status_code == 204
    assert client.get("/api/reportes", headers=headers).json() == []

    # El historial sigue ahí para quien lo pida.
    con_revisados = client.get("/api/reportes?incluir_revisados=true", headers=headers).json()
    assert len(con_revisados) == 1
    assert con_revisados[0]["pendientes"] == 0
    assert con_revisados[0]["comentarios"][0]["revisado_en"] is not None

    # Cerrar dos veces no tiene nada que cerrar.
    assert client.post(f"/api/reportes/{question.id}/revisado", headers=headers).status_code == 404
