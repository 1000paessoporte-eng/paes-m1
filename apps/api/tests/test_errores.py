"""El buzón de errores del navegador.

Hasta ahora, un error de JavaScript en el teléfono de un estudiante no dejaba
rastro en ninguna parte: la página quedaba en blanco y nosotros nos
enterábamos si esa persona se molestaba en escribirnos.
"""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.errores.models import ErrorCliente
from paes_api.modules.users.models import User


def _hacer_admin(db: Session, email: str) -> None:
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    user.is_admin = True
    db.commit()


def test_se_reporta_sin_sesion(client: TestClient, db_session: Session) -> None:
    """La mayoría de los errores revienta antes del login. De esos era
    justamente de los que nunca nos enterábamos."""
    resp = client.post(
        "/api/errores",
        json={"mensaje": "Cannot read properties of undefined", "ruta": "/panel"},
    )
    assert resp.status_code == 204, resp.text

    fila = db_session.execute(select(ErrorCliente)).scalars().one()
    assert fila.user_id is None
    assert fila.veces == 1


def test_el_mismo_error_suma_en_vez_de_multiplicarse(client: TestClient, db_session) -> None:
    """Un bucle de render dispara un reporte por cuadro. Sin agrupar, la tabla
    se llena de copias idénticas y tapa todo lo demás."""
    for _ in range(5):
        client.post("/api/errores", json={"mensaje": "boom", "ruta": "/examen"})

    filas = db_session.execute(select(ErrorCliente)).scalars().all()
    assert len(filas) == 1
    assert filas[0].veces == 5


def test_la_ruta_pierde_query_y_fragmento(client: TestClient, db_session) -> None:
    """`/examen?intento=42` y `/examen?intento=43` son el mismo error. Y el
    query string puede traer datos de la persona."""
    client.post("/api/errores", json={"mensaje": "boom", "ruta": "/examen?intento=42"})
    client.post("/api/errores", json={"mensaje": "boom", "ruta": "/examen?intento=43"})

    filas = db_session.execute(select(ErrorCliente)).scalars().all()
    assert len(filas) == 1
    assert filas[0].ruta == "/examen"
    assert filas[0].veces == 2


def test_una_ruta_que_no_es_ruta_no_se_guarda_tal_cual(client: TestClient, db_session) -> None:
    """El campo llega del navegador: nada garantiza que sea una ruta nuestra."""
    client.post(
        "/api/errores",
        json={"mensaje": "boom", "ruta": "https://otro-sitio.cl/lo-que-sea"},
    )
    fila = db_session.execute(select(ErrorCliente)).scalars().one()
    assert fila.ruta == "/"


def test_el_panel_es_solo_del_admin(client: TestClient, register_user, db_session) -> None:
    assert client.get("/api/errores").status_code == 401

    headers, _ = register_user(email="curiosa@milpaes.cl")
    # 404 y no 403: para una cuenta normal el panel ni siquiera existe.
    assert client.get("/api/errores", headers=headers).status_code == 404

    _hacer_admin(db_session, "curiosa@milpaes.cl")
    resp = client.get("/api/errores", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_el_panel_ordena_por_lo_que_mas_duele(
    client: TestClient, register_user, db_session
) -> None:
    headers, _ = register_user(email="jefa@milpaes.cl")
    _hacer_admin(db_session, "jefa@milpaes.cl")

    for _ in range(3):
        client.post("/api/errores", json={"mensaje": "raro", "ruta": "/meta"})
    for _ in range(9):
        client.post("/api/errores", json={"mensaje": "grave", "ruta": "/examen"})

    panel = client.get("/api/errores", headers=headers).json()
    assert [e["mensaje"] for e in panel] == ["grave", "raro"]
    assert panel[0]["veces"] == 9
