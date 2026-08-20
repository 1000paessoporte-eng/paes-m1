"""Borrar la cuenta.

Estaba solo en la política de privacidad como "escríbenos a hola@". Lo que se
fija acá es que borre de verdad --no que esconda-- y que no lo pueda hacer
cualquiera que encuentre una sesión abierta.
"""

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from paes_api.modules.exam_focus.models import AttemptStatus, ExamAttempt
from paes_api.modules.metrics.models import PageView
from paes_api.modules.users.models import User


def test_pide_la_contrasena(client: TestClient, register_user) -> None:
    """Borrar es irreversible: no puede depender solo de que alguien dejó la
    sesión abierta en un computador prestado."""
    headers, _ = register_user(email="borrar@milpaes.cl", password="clave1234")

    assert client.request("DELETE", "/api/auth/me", headers=headers, json={}).status_code == 401
    assert client.request(
        "DELETE", "/api/auth/me", headers=headers, json={"password": "otra"}
    ).status_code == 401


def test_borra_la_cuenta_y_lo_que_cuelga_de_ella(
    client: TestClient, db_session: Session, register_user
) -> None:
    headers, _ = register_user(email="chao@milpaes.cl", password="clave1234")
    user = db_session.execute(select(User).where(User.email == "chao@milpaes.cl")).scalar_one()
    db_session.add(
        ExamAttempt(user_id=user.id, duration_limit_seconds=8400, status=AttemptStatus.SUBMITTED)
    )
    db_session.commit()

    resp = client.request(
        "DELETE", "/api/auth/me", headers=headers, json={"password": "clave1234"}
    )
    assert resp.status_code == 204

    # Se BORRA, no se esconde: una fila con el correo dentro sigue siendo el dato.
    assert db_session.execute(
        select(func.count(User.id)).where(User.email == "chao@milpaes.cl")
    ).scalar_one() == 0
    assert db_session.execute(
        select(func.count(ExamAttempt.id)).where(ExamAttempt.user_id == user.id)
    ).scalar_one() == 0


def test_la_visita_se_conserva_sin_dueno(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Las visitas son estadística agregada del sitio: sin user_id ya no
    identifican a nadie, y borrarlas falsearía el tráfico histórico."""
    headers, _ = register_user(email="visita@milpaes.cl", password="clave1234")
    user = db_session.execute(select(User).where(User.email == "visita@milpaes.cl")).scalar_one()
    db_session.add(PageView(path="/panel", visitor_id="visitante-1234", user_id=user.id))
    db_session.commit()

    client.request("DELETE", "/api/auth/me", headers=headers, json={"password": "clave1234"})

    visita = db_session.execute(select(PageView)).scalar_one()
    assert visita.user_id is None, "la visita pierde el dueño"
    assert visita.path == "/panel", "pero sigue contando como tráfico"


def test_sin_sesion_no_se_borra_nada(client: TestClient) -> None:
    assert client.request("DELETE", "/api/auth/me", json={"password": "x"}).status_code == 401
