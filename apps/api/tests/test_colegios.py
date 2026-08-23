"""El plan Colegios: quién ve qué, y qué pasa cuando alguien se va."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


def test_crea_curso_y_recibe_codigo(client: TestClient, register_user) -> None:
    headers, _ = register_user(email="profe@milpaes.cl")

    resp = client.post("/api/colegio", json={"nombre": "Liceo A-1"}, headers=headers)
    assert resp.status_code == 201, resp.text
    cuerpo = resp.json()

    assert cuerpo["es_profesor"] is True
    assert cuerpo["alumnos"] == 0
    # El código es lo que el profesor le dicta al curso: si no vuelve, no hay
    # forma de que nadie se sume.
    assert cuerpo["codigo"] and len(cuerpo["codigo"]) == 6


def test_el_alumno_no_recibe_el_codigo(client: TestClient, register_user) -> None:
    """El código deja de ser del profesor si cualquiera lo puede leer.

    Un alumno con el código lo reparte por WhatsApp y el panel del profesor
    pasa a mostrar gente que no es de su curso.
    """
    profe, _ = register_user(email="profe@milpaes.cl")
    codigo = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()["codigo"]

    alumno, _ = register_user(email="alumna@milpaes.cl")
    resp = client.post("/api/colegio/unirse", json={"codigo": codigo}, headers=alumno)
    assert resp.status_code == 200, resp.text
    assert resp.json()["codigo"] is None
    assert resp.json()["es_profesor"] is False

    # Y el profesor ahora ve una persona en su curso.
    mio = client.get("/api/colegio", headers=profe).json()
    assert mio["alumnos"] == 1


def test_codigo_inexistente_da_404(client: TestClient, register_user) -> None:
    headers, _ = register_user(email="alguien@milpaes.cl")
    resp = client.post("/api/colegio/unirse", json={"codigo": "ZZZZZZ"}, headers=headers)
    assert resp.status_code == 404


def test_no_se_puede_estar_en_dos_cursos(client: TestClient, register_user) -> None:
    profe, _ = register_user(email="profe@milpaes.cl")
    codigo = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()["codigo"]

    alumno, _ = register_user(email="alumna@milpaes.cl")
    client.post("/api/colegio/unirse", json={"codigo": codigo}, headers=alumno)
    otra = client.post("/api/colegio/unirse", json={"codigo": codigo}, headers=alumno)
    assert otra.status_code == 409


def test_el_alumno_no_ve_la_lista_del_curso(client: TestClient, register_user) -> None:
    """La tabla trae correos de compañeros. Solo la ve el profesor."""
    profe, _ = register_user(email="profe@milpaes.cl")
    codigo = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()["codigo"]

    alumno, _ = register_user(email="alumna@milpaes.cl")
    client.post("/api/colegio/unirse", json={"codigo": codigo}, headers=alumno)

    assert client.get("/api/colegio/alumnos", headers=alumno).status_code == 403
    assert client.get("/api/colegio/ejes", headers=alumno).status_code == 403

    lista = client.get("/api/colegio/alumnos", headers=profe)
    assert lista.status_code == 200
    assert [a["email"] for a in lista.json()] == ["alumna@milpaes.cl"]
    # Sin actividad todavía: los contadores existen en cero, no en null.
    assert lista.json()[0]["ensayos"] == 0
    assert lista.json()[0]["mejor_puntaje"] is None


def test_sin_curso_la_consulta_devuelve_null(client: TestClient, register_user) -> None:
    headers, _ = register_user(email="sola@milpaes.cl")
    resp = client.get("/api/colegio", headers=headers)
    assert resp.status_code == 200
    assert resp.json() is None


def test_salir_no_borra_nada_de_la_cuenta(client: TestClient, register_user) -> None:
    profe, _ = register_user(email="profe@milpaes.cl")
    codigo = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()["codigo"]

    alumno, _ = register_user(email="alumna@milpaes.cl")
    client.post("/api/colegio/unirse", json={"codigo": codigo}, headers=alumno)
    assert client.post("/api/colegio/salir", headers=alumno).status_code == 204

    assert client.get("/api/colegio", headers=alumno).json() is None
    # La cuenta sigue en pie: puede volver a entrar a otro curso.
    assert client.get("/api/panel", headers=alumno).status_code in (200, 404)
    assert client.get("/api/colegio", headers=profe).json()["alumnos"] == 0


def test_agendar_ensayo_y_verlo_desde_los_dos_lados(
    client: TestClient, register_user
) -> None:
    profe, _ = register_user(email="profe@milpaes.cl")
    codigo = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()["codigo"]
    alumno, _ = register_user(email="alumna@milpaes.cl")
    client.post("/api/colegio/unirse", json={"codigo": codigo}, headers=alumno)

    viernes = (datetime.now(UTC).date() + timedelta(days=3)).isoformat()
    creado = client.post(
        "/api/colegio/ensayos",
        json={"titulo": "Ensayo de M1", "subject": "m1", "fecha": viernes},
        headers=profe,
    )
    assert creado.status_code == 201, creado.text

    # El profesor ve cuántos lo rindieron; el alumno, si lo rindió él.
    del_profe = client.get("/api/colegio/ensayos", headers=profe).json()
    assert del_profe[0]["rendido_por"] == 0
    del_alumno = client.get("/api/colegio/ensayos", headers=alumno).json()
    assert del_alumno[0]["lo_rendi"] is False
    assert del_alumno[0]["titulo"] == "Ensayo de M1"


def test_el_alumno_no_agenda_ensayos(client: TestClient, register_user) -> None:
    profe, _ = register_user(email="profe@milpaes.cl")
    codigo = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()["codigo"]
    alumno, _ = register_user(email="alumna@milpaes.cl")
    client.post("/api/colegio/unirse", json={"codigo": codigo}, headers=alumno)

    resp = client.post(
        "/api/colegio/ensayos",
        json={
            "titulo": "Sin clases el viernes",
            "subject": "m1",
            "fecha": datetime.now(UTC).date().isoformat(),
        },
        headers=alumno,
    )
    assert resp.status_code == 403


def test_un_profesor_no_borra_la_agenda_de_otro_curso(
    client: TestClient, register_user
) -> None:
    """Sin comprobar el colegio, bastaba probar números para borrar ajeno."""
    una, _ = register_user(email="profe1@milpaes.cl")
    client.post("/api/colegio", json={"nombre": "Liceo A-1"}, headers=una)
    ensayo = client.post(
        "/api/colegio/ensayos",
        json={
            "titulo": "Ensayo de M1",
            "subject": "m1",
            "fecha": datetime.now(UTC).date().isoformat(),
        },
        headers=una,
    ).json()

    otro, _ = register_user(email="profe2@milpaes.cl")
    client.post("/api/colegio", json={"nombre": "Liceo B-2"}, headers=otro)

    resp = client.delete(f"/api/colegio/ensayos/{ensayo['id']}", headers=otro)
    assert resp.status_code == 404
    # Y sigue ahí para quien sí es su dueño.
    assert len(client.get("/api/colegio/ensayos", headers=una).json()) == 1


def _hacer_admin(db_session, email: str) -> None:
    from sqlalchemy import select

    from paes_api.modules.users.models import User

    user = db_session.execute(select(User).where(User.email == email)).scalar_one()
    user.is_admin = True
    db_session.commit()


def test_el_plan_del_curso_le_da_pro_a_sus_alumnos(
    client: TestClient, register_user, db_session
) -> None:
    """Es lo que compra el colegio. Sin esto, el plan cobraba por nada."""
    profe, _ = register_user(email="profe@milpaes.cl")
    curso = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()
    alumno, _ = register_user(email="alumna@milpaes.cl")
    client.post("/api/colegio/unirse", json={"codigo": curso["codigo"]}, headers=alumno)

    # Antes de que el colegio pague, la alumna es del plan Gratis.
    assert client.get("/api/plan", headers=alumno).json()["plan"] == "gratis"

    _hacer_admin(db_session, "profe@milpaes.cl")
    fin = (datetime.now(UTC).date() + timedelta(days=200)).isoformat()
    resp = client.put(
        f"/api/colegio/admin/{curso['id']}/plan",
        json={"plan_hasta": fin},
        headers=profe,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["alumnos"] == 1

    plan = client.get("/api/plan", headers=alumno).json()
    assert plan["plan"] == "colegios"
    # Y con los límites de Pro: ensayos sin tope.
    assert plan["ensayos_limite"] is None
    assert plan["carreras_limite"] == 10


def test_el_plan_vencido_no_sigue_dando_pro(
    client: TestClient, register_user, db_session
) -> None:
    profe, _ = register_user(email="profe@milpaes.cl")
    curso = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()
    alumno, _ = register_user(email="alumna@milpaes.cl")
    client.post("/api/colegio/unirse", json={"codigo": curso["codigo"]}, headers=alumno)

    _hacer_admin(db_session, "profe@milpaes.cl")
    ayer = (datetime.now(UTC).date() - timedelta(days=1)).isoformat()
    client.put(
        f"/api/colegio/admin/{curso['id']}/plan",
        json={"plan_hasta": ayer},
        headers=profe,
    )

    assert client.get("/api/plan", headers=alumno).json()["plan"] == "gratis"


def test_el_profesor_no_se_activa_el_plan_solo(
    client: TestClient, register_user
) -> None:
    profe, _ = register_user(email="profe@milpaes.cl")
    curso = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()

    fin = (datetime.now(UTC).date() + timedelta(days=365)).isoformat()
    resp = client.put(
        f"/api/colegio/admin/{curso['id']}/plan",
        json={"plan_hasta": fin},
        headers=profe,
    )
    assert resp.status_code == 404
    assert client.get("/api/colegio/admin/todos", headers=profe).status_code == 404


def test_los_ejes_del_curso_salen_de_los_ensayos_entregados(
    client: TestClient, register_user, db_session
) -> None:
    """El dato que un profesor no puede sacar de una tabla de puntajes.

    Treinta alumnos con 600 puntos pueden estar fallando todos en el mismo
    eje, y eso decide qué se pasa la clase del lunes.
    """
    from sqlalchemy import select

    from paes_api.modules.content.models import Alternative, Difficulty, Question
    from paes_api.modules.exam_focus.models import (
        AttemptStatus,
        ExamAnswer,
        ExamAttempt,
    )
    from paes_api.modules.skill_tree.models import SkillAxis, SkillNode
    from paes_api.modules.users.models import User

    profe, _ = register_user(email="profe@milpaes.cl")
    curso = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()
    alumno, _ = register_user(email="alumna@milpaes.cl")
    client.post("/api/colegio/unirse", json={"codigo": curso["codigo"]}, headers=alumno)
    alumna = db_session.execute(
        select(User).where(User.email == "alumna@milpaes.cl")
    ).scalar_one()

    nodo = SkillNode(
        code="n_geo", name="Geometría", axis=SkillAxis.GEOMETRIA, tier=1
    )
    db_session.add(nodo)
    db_session.flush()

    intento = ExamAttempt(user_id=alumna.id, status=AttemptStatus.SUBMITTED)
    db_session.add(intento)
    db_session.flush()

    # Cuatro respuestas, una correcta: 25%.
    for i in range(4):
        q = Question(skill_node_id=nodo.id, difficulty=Difficulty.MEDIO, stem=f"P{i}")
        db_session.add(q)
        db_session.flush()
        alt = Alternative(question_id=q.id, label="A", text="x", is_correct=(i == 0))
        db_session.add(alt)
        db_session.flush()
        db_session.add(
            ExamAnswer(
                attempt_id=intento.id, question_id=q.id, selected_alternative_id=alt.id
            )
        )
    db_session.commit()

    ejes = client.get("/api/colegio/ejes", headers=profe).json()
    assert len(ejes) == 1
    assert ejes[0]["eje"] == "geometria"
    assert ejes[0]["nombre"] == "Geometría"
    assert ejes[0]["respuestas"] == 4
    assert ejes[0]["porcentaje"] == 25


def test_los_ejes_no_cuentan_ensayos_a_medias(
    client: TestClient, register_user, db_session
) -> None:
    """Un ensayo en curso tiene las preguntas del final sin responder.

    Contarlas hundiría justo los ejes que la prueba deja para el final.
    """
    from sqlalchemy import select

    from paes_api.modules.content.models import Alternative, Difficulty, Question
    from paes_api.modules.exam_focus.models import (
        AttemptStatus,
        ExamAnswer,
        ExamAttempt,
    )
    from paes_api.modules.skill_tree.models import SkillAxis, SkillNode
    from paes_api.modules.users.models import User

    profe, _ = register_user(email="profe@milpaes.cl")
    curso = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()
    alumno, _ = register_user(email="alumna@milpaes.cl")
    client.post("/api/colegio/unirse", json={"codigo": curso["codigo"]}, headers=alumno)
    alumna = db_session.execute(
        select(User).where(User.email == "alumna@milpaes.cl")
    ).scalar_one()

    nodo = SkillNode(code="n_alg", name="Álgebra", axis=SkillAxis.ALGEBRA, tier=1)
    db_session.add(nodo)
    db_session.flush()
    q = Question(skill_node_id=nodo.id, difficulty=Difficulty.MEDIO, stem="P")
    db_session.add(q)
    db_session.flush()
    alt = Alternative(question_id=q.id, label="A", text="x", is_correct=False)
    db_session.add(alt)

    enCurso = ExamAttempt(user_id=alumna.id, status=AttemptStatus.IN_PROGRESS)
    db_session.add(enCurso)
    db_session.flush()
    db_session.add(
        ExamAnswer(
            attempt_id=enCurso.id, question_id=q.id, selected_alternative_id=alt.id
        )
    )
    db_session.commit()

    assert client.get("/api/colegio/ejes", headers=profe).json() == []


def test_la_tabla_dice_cuantos_dias_lleva_sin_rendir(
    client: TestClient, register_user, db_session
) -> None:
    """Es la pregunta con la que un profesor abre esta pantalla.

    Viaja calculado desde la API y no se deduce en el navegador: leer el reloj
    durante el render da un número distinto en cada dibujado.
    """
    from sqlalchemy import select

    from paes_api.modules.exam_focus.models import AttemptStatus, ExamAttempt
    from paes_api.modules.users.models import User

    profe, _ = register_user(email="profe@milpaes.cl")
    curso = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()
    alumno, _ = register_user(email="alumna@milpaes.cl")
    client.post("/api/colegio/unirse", json={"codigo": curso["codigo"]}, headers=alumno)
    alumna = db_session.execute(
        select(User).where(User.email == "alumna@milpaes.cl")
    ).scalar_one()

    db_session.add(
        ExamAttempt(
            user_id=alumna.id,
            status=AttemptStatus.SUBMITTED,
            estimated_score=620,
            finished_at=datetime.now(UTC) - timedelta(days=9),
        )
    )
    db_session.commit()

    fila = client.get("/api/colegio/alumnos", headers=profe).json()[0]
    assert fila["ensayos"] == 1
    assert fila["mejor_puntaje"] == 620
    assert fila["dias_sin_rendir"] == 9


def test_el_profesor_que_se_sale_recupera_su_curso(
    client: TestClient, register_user
) -> None:
    """Salirse del curso propio no puede ser una puerta sin retorno.

    El código solo se le muestra al profesor, así que un curso cuyo creador se
    sale y vuelve como alumno queda sin nadie que pueda repartir el código,
    agendar ensayos ni mirar el avance de los treinta que están adentro.
    """
    profe, _ = register_user(email="profe@milpaes.cl")
    codigo = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()["codigo"]

    assert client.post("/api/colegio/salir", headers=profe).status_code == 204
    assert client.get("/api/colegio", headers=profe).json() is None

    vuelta = client.post("/api/colegio/unirse", json={"codigo": codigo}, headers=profe)
    assert vuelta.status_code == 200, vuelta.text
    assert vuelta.json()["es_profesor"] is True
    assert vuelta.json()["codigo"] == codigo

    # Y con el rol de vuelta, el panel del curso vuelve a abrirse.
    assert client.get("/api/colegio/alumnos", headers=profe).status_code == 200
