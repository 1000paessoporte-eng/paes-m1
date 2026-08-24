"""Un ensayo contestado tan rápido que no da tiempo ni de leerlo.

No es trampa ni un agujero: es alguien haciendo clic sin leer, que es un
comportamiento normal y frecuente. Pero sus puntos no dicen nada de lo que esa
persona sabe, y contarlos ensucia su propio historial, la analítica del
producto y --desde el plan Colegios-- la tabla con la que un profesor decide a
quién ir a buscar.

El ensayo se rinde igual, se corrige igual y se revisa igual. Solo deja de
contar donde un número falso haría daño.
"""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from paes_api.modules.content.models import Alternative, Difficulty, Question
from paes_api.modules.exam_focus import service
from paes_api.modules.exam_focus.models import AttemptStatus, ExamAttempt
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode, Subject


def _banco(db: Session, cuantas: int = 6) -> SkillNode:
    node = SkillNode(
        code="n_repr", name="Tema", axis=SkillAxis.NUMEROS, tier=1, unlock_threshold=0.75
    )
    db.add(node)
    db.flush()
    for i in range(cuantas):
        q = Question(skill_node_id=node.id, difficulty=Difficulty.MEDIO, stem=f"P{i}")
        db.add(q)
        db.flush()
        db.add_all(
            [
                Alternative(question_id=q.id, label="A", text="ok", is_correct=True),
                Alternative(question_id=q.id, label="B", text="mal", is_correct=False),
            ]
        )
    db.commit()
    return node


def _intento(db: Session, user_id: int, segundos: int) -> ExamAttempt:
    """Un intento que empezó hace `segundos` y se entrega ahora."""
    a = ExamAttempt(
        user_id=user_id,
        started_at=datetime.now(UTC) - timedelta(seconds=segundos),
        duration_limit_seconds=2585,
        status=AttemptStatus.IN_PROGRESS,
        subject=Subject.M1,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_veinte_preguntas_en_veintiun_segundos_no_es_representativo(
    client: TestClient, db_session: Session, register_user
) -> None:
    """El caso que lo motivó, tal cual apareció probando el flujo real."""
    _banco(db_session)
    headers, user = register_user(email="rapido@milpaes.cl")

    inicio = client.post(
        "/api/exam/start",
        json={"subject": "m1", "question_count": 6, "pace": "oficial"},
        headers=headers,
    ).json()
    aid = inicio["attempt_id"]

    for q in inicio["questions"]:
        client.post(
            f"/api/exam/{aid}/answer",
            json={
                "question_id": q["id"],
                "selected_alternative_id": q["alternatives"][0]["id"],
                "seconds_spent": 1,
            },
            headers=headers,
        )

    resp = client.post(f"/api/exam/{aid}/submit", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["representativo"] is False


def test_un_ensayo_a_ritmo_normal_si_cuenta(db_session: Session, register_user) -> None:
    _headers, user = register_user(email="normal@milpaes.cl")
    # 6 preguntas en 20 minutos: 200 s cada una, por encima del ritmo oficial.
    a = _intento(db_session, user["id"], segundos=1200)
    a.finished_at = datetime.now(UTC)
    assert service._es_representativo(a, respondidas=6) is True


def test_el_que_responde_poco_y_abandona_sigue_contando(
    db_session: Session, register_user
) -> None:
    """Rendir poco no es rendir rápido.

    Quien contesta tres preguntas con calma y cierra la pestaña no hizo clic al
    azar: esas tres respuestas dicen algo. Medir contra el total de preguntas
    en vez de contra las respondidas lo marcaría como no representativo.
    """
    _headers, user = register_user(email="abandona@milpaes.cl")
    a = _intento(db_session, user["id"], segundos=600)
    a.finished_at = datetime.now(UTC)
    assert service._es_representativo(a, respondidas=3) is True


def test_un_ensayo_sin_ninguna_respuesta_no_cuenta(
    db_session: Session, register_user
) -> None:
    """Un ensayo vacío no es apurado: es vacío, y no dice nada del alumno.

    Este caso devolvía True con el argumento de que "sin respuestas no hay
    nada que juzgar". Es cierto del RITMO --no hay ritmo que medir-- pero la
    bandera no responde "¿fue apurado?", responde "¿este ensayo cuenta?".

    De los 42 ensayos entregados en producción, 26 no tenían ni una respuesta
    (el 62%) y todos entraban al historial, al mejor puntaje, a la analítica y
    al panel del profesor con un puntaje medio de 160 -- el piso de la escala,
    no una medición. Para el alumno típico, la mayor parte de su historial
    eran ensayos que nunca respondió.
    """
    _headers, user = register_user(email="vacio@milpaes.cl")
    a = _intento(db_session, user["id"], segundos=5)
    a.finished_at = datetime.now(UTC)
    assert service._es_representativo(a, respondidas=0) is False

    # Y con calma tampoco: el tiempo no arregla la ausencia de respuestas.
    b = _intento(db_session, user["id"], segundos=3600)
    b.finished_at = datetime.now(UTC)
    assert service._es_representativo(b, respondidas=0) is False


def test_una_sola_respuesta_con_calma_si_cuenta(
    db_session: Session, register_user
) -> None:
    """El corte está en cero, no en "pocas": una respuesta pensada dice algo."""
    _headers, user = register_user(email="una-sola@milpaes.cl")
    a = _intento(db_session, user["id"], segundos=300)
    a.finished_at = datetime.now(UTC)
    assert service._es_representativo(a, respondidas=1) is True


def test_el_umbral_es_relativo_al_ritmo_de_cada_prueba(
    db_session: Session, register_user
) -> None:
    """Cada prueba tiene su propio ritmo oficial del DEMRE.

    Un fijo en segundos trataría igual a Competencia Lectora --que da tiempo de
    leer un texto largo-- y a matemática.
    """
    _headers, user = register_user(email="ritmos@milpaes.cl")
    a = _intento(db_session, user["id"], segundos=60)
    a.finished_at = datetime.now(UTC)

    from paes_api.modules.exam_focus.scoring import segundos_por_pregunta

    a.subject = Subject.M1
    limite_m1 = segundos_por_pregunta(Subject.M1) * service.FRACCION_MINIMA_DE_RITMO
    a.subject = Subject.LECTORA
    limite_lectora = (
        segundos_por_pregunta(Subject.LECTORA) * service.FRACCION_MINIMA_DE_RITMO
    )
    assert limite_m1 != limite_lectora
