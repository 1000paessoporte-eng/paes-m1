from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.metrics.models import PageView
from paes_api.modules.users.models import LoginEvent, User


def _hacer_admin(db: Session, email: str) -> User:
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    user.is_admin = True
    db.commit()
    return user


def test_metrics_requiere_sesion(client: TestClient) -> None:
    assert client.get("/api/admin/metrics").status_code == 401


def test_metrics_oculto_para_cuenta_normal(client: TestClient, register_user) -> None:
    headers, _ = register_user(email="normal@milpaes.cl")
    resp = client.get("/api/admin/metrics", headers=headers)
    # 404 y no 403: una cuenta normal no debe enterarse de que el panel existe.
    assert resp.status_code == 404


def test_metrics_para_admin(
    client: TestClient, register_user, db_session: Session
) -> None:
    headers, _ = register_user(email="jefa@milpaes.cl")
    _hacer_admin(db_session, "jefa@milpaes.cl")

    resp = client.get("/api/admin/metrics", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert set(body) >= {"usuarios", "sesiones", "visitas", "contenido"}
    assert body["usuarios"]["registros"]["total"] == 1
    assert body["usuarios"]["ultimos"][0]["email"] == "jefa@milpaes.cl"


def test_registro_y_login_dejan_rastro(
    client: TestClient, register_user, db_session: Session
) -> None:
    register_user(email="rastro@milpaes.cl", password="clave1234")
    client.post(
        "/api/auth/login", json={"email": "rastro@milpaes.cl", "password": "clave1234"}
    )

    eventos = db_session.execute(select(LoginEvent)).scalars().all()
    # Uno por el registro y otro por el login.
    assert len(eventos) == 2
    assert {e.method for e in eventos} == {"password"}

    user = db_session.execute(
        select(User).where(User.email == "rastro@milpaes.cl")
    ).scalar_one()
    assert user.last_login_at is not None


def test_pageview_publico_sin_sesion(client: TestClient, db_session: Session) -> None:
    resp = client.post(
        "/api/metrics/pageview", json={"path": "/", "visitor_id": "abcdefgh1234"}
    )
    assert resp.status_code == 204

    vista = db_session.execute(select(PageView)).scalar_one()
    assert vista.path == "/"
    assert vista.user_id is None


def test_pageview_con_sesion_queda_identificada(
    client: TestClient, register_user, db_session: Session
) -> None:
    headers, user = register_user(email="visita@milpaes.cl")
    resp = client.post(
        "/api/metrics/pageview",
        json={"path": "/examen", "visitor_id": "abcdefgh1234"},
        headers=headers,
    )
    assert resp.status_code == 204

    vista = db_session.execute(select(PageView)).scalar_one()
    assert vista.user_id == user["id"]


def test_pageview_descarta_url_externa_y_query(
    client: TestClient, db_session: Session
) -> None:
    client.post(
        "/api/metrics/pageview",
        json={"path": "https://otro-sitio.cl/robo", "visitor_id": "abcdefgh1234"},
    )
    assert db_session.execute(select(PageView)).first() is None

    # El token de restablecer contraseña viaja en la query: no debe guardarse.
    client.post(
        "/api/metrics/pageview",
        json={"path": "/restablecer-contrasena?token=secreto", "visitor_id": "abcdefgh1234"},
    )
    vista = db_session.execute(select(PageView)).scalar_one()
    assert vista.path == "/restablecer-contrasena"


def test_metricas_cuentan_visitas_y_entradas(
    client: TestClient, register_user, db_session: Session
) -> None:
    headers, _ = register_user(email="jefe@milpaes.cl")
    _hacer_admin(db_session, "jefe@milpaes.cl")

    for path in ["/", "/", "/examen"]:
        client.post("/api/metrics/pageview", json={"path": path, "visitor_id": "visitante-1"})
    client.post("/api/metrics/pageview", json={"path": "/", "visitor_id": "visitante-2"})

    body = client.get("/api/admin/metrics", headers=headers).json()

    assert body["visitas"]["vistas"]["total"] == 4
    assert body["visitas"]["visitantes"]["total"] == 2
    assert body["visitas"]["top_rutas"][0]["path"] == "/"
    assert body["visitas"]["top_rutas"][0]["visitas"] == 3
    # Ninguna de esas visitas llevaba sesión.
    assert body["visitas"]["anonimas_7"] == 4
    # El registro cuenta como entrada.
    assert body["sesiones"]["entradas"]["total"] == 1
    assert body["sesiones"]["activos_7"] == 1


def test_contenido_sin_datos_no_inventa_ceros(
    client: TestClient, register_user, db_session: Session
) -> None:
    headers, _ = register_user(email="jefa2@milpaes.cl")
    _hacer_admin(db_session, "jefa2@milpaes.cl")

    contenido = client.get("/api/admin/metrics", headers=headers).json()["contenido"]
    assert contenido["ensayos"]["total"] == 0
    # Sin ensayos rendidos no hay promedio: null, no 0.
    assert contenido["puntaje_promedio"] is None
    assert contenido["tasa_acierto_global"] is None
    assert contenido["preguntas_mas_falladas"] == []
