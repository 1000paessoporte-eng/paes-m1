"""La cotización del plan Colegios: el formulario público y su panel.

Un colegio no compra con tarjeta --pide cotización, la aprueba el sostenedor
y paga con factura-- así que este formulario es la puerta de entrada de la
venta. Lo que se prueba es que no se pierda ninguna solicitud: ni por un
correo que no salió, ni porque quien la llenó no tenía cuenta.
"""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.colegios.models import SolicitudColegio
from paes_api.modules.users.models import User

SOLICITUD = {
    "establecimiento": "Liceo Bicentenario de Talca",
    "contacto": "Carmen Rojas",
    "cargo": "Jefa de UTP",
    "email": "utp@liceodetalca.cl",
    "telefono": "+56 9 1234 5678",
    "comuna": "Talca",
    "alumnos": 90,
    "mensaje": "Tenemos tres cursos de cuarto medio.",
}


def _hacer_admin(db: Session, email: str) -> User:
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    user.is_admin = True
    db.commit()
    return user


def test_un_colegio_pide_cotizacion_sin_tener_cuenta(
    client: TestClient, db_session: Session
) -> None:
    """Pedirle que se registre antes de saber el precio sería poner el
    formulario más largo delante de la pregunta más simple."""
    r = client.post("/api/colegio/cotizacion", json=SOLICITUD)
    assert r.status_code == 201, r.text
    assert r.json()["establecimiento"] == SOLICITUD["establecimiento"]
    assert r.json()["atendida"] is False

    guardada = db_session.execute(select(SolicitudColegio)).scalar_one()
    assert guardada.alumnos == 90
    assert guardada.email == "utp@liceodetalca.cl"


def test_si_el_correo_falla_la_solicitud_igual_queda_guardada(
    client: TestClient, db_session: Session, monkeypatch
) -> None:
    """Que el aviso no salga se arregla mirando el panel. Que un colegio reciba
    un error después de llenar el formulario es perder la venta con la persona
    ya convencida."""
    from paes_api.core.email import CorreoNoEnviado
    from paes_api.modules.colegios import service

    def explota(*a, **k):
        raise CorreoNoEnviado("proveedor caído")

    monkeypatch.setattr(service, "send_email", explota)

    assert client.post("/api/colegio/cotizacion", json=SOLICITUD).status_code == 201
    assert db_session.execute(select(SolicitudColegio)).scalar_one() is not None


def test_el_acuse_va_al_colegio_y_el_aviso_al_equipo(
    client: TestClient, monkeypatch
) -> None:
    from paes_api.modules.colegios import service
    from paes_api.modules.correos.service import CONTACTO

    enviados: list[tuple] = []
    monkeypatch.setattr(service, "send_email", lambda *a, **k: enviados.append(a))

    client.post("/api/colegio/cotizacion", json=SOLICITUD)

    destinos = [e[0] for e in enviados]
    assert destinos == [CONTACTO, "utp@liceodetalca.cl"]
    #: El aviso interno trae lo necesario para responder desde el teléfono.
    aviso = enviados[0][2]
    assert "90" in aviso and "Jefa de UTP" in aviso and "utp@liceodetalca.cl" in aviso
    #: El acuse NO promete un precio: la cotización la hace una persona.
    acuse = enviados[1][2]
    assert "día hábil" in acuse


def test_una_cantidad_imposible_se_rechaza(client: TestClient) -> None:
    for alumnos in (0, 99999):
        r = client.post("/api/colegio/cotizacion", json={**SOLICITUD, "alumnos": alumnos})
        assert r.status_code == 422


def test_un_correo_mal_escrito_se_rechaza(client: TestClient) -> None:
    r = client.post("/api/colegio/cotizacion", json={**SOLICITUD, "email": "no-es-correo"})
    assert r.status_code == 422


def test_el_panel_las_lista_y_las_marca_atendidas(
    client: TestClient, db_session: Session, register_user
) -> None:
    client.post("/api/colegio/cotizacion", json=SOLICITUD)
    headers, _ = register_user(email="jefe@milpaes.cl")
    _hacer_admin(db_session, "jefe@milpaes.cl")

    listado = client.get("/api/colegio/admin/cotizaciones", headers=headers)
    assert listado.status_code == 200
    (fila,) = listado.json()
    assert fila["contacto"] == "Carmen Rojas" and fila["atendida"] is False

    marcada = client.put(
        f"/api/colegio/admin/cotizaciones/{fila['id']}?atendida=true", headers=headers
    )
    assert marcada.status_code == 200 and marcada.json()["atendida"] is True


def test_las_cotizaciones_no_son_publicas(client: TestClient, register_user) -> None:
    """Traen nombre, correo y teléfono de personas: solo las ve un admin."""
    assert client.get("/api/colegio/admin/cotizaciones").status_code == 401
    headers, _ = register_user(email="curiosa@milpaes.cl")
    #: 404 y no 403: para una cuenta normal el panel no revela ni que existe
    #: (ver `get_current_admin`).
    assert client.get("/api/colegio/admin/cotizaciones", headers=headers).status_code == 404
