from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.leads.models import Lead


def test_deja_correo_sin_cuenta(client: TestClient, db_session: Session) -> None:
    resp = client.post("/api/leads", json={"email": "Alguien@Ejemplo.CL", "source": "demo"})
    assert resp.status_code == 201
    assert resp.json() == {"ok": True}

    guardado = db_session.execute(select(Lead)).scalar_one()
    # Normalizado: si no, el mismo correo entra dos veces con otra caja.
    assert guardado.email == "alguien@ejemplo.cl"
    assert guardado.source == "demo"


def test_repetir_el_correo_no_duplica_ni_falla(client: TestClient, db_session: Session) -> None:
    """Quien vuelve a la demo y deja el correo otra vez no tiene por qué ver
    un error: para él es la misma acción."""
    for _ in range(3):
        assert client.post("/api/leads", json={"email": "repe@ejemplo.cl"}).status_code == 201

    assert len(db_session.execute(select(Lead)).scalars().all()) == 1


def test_correo_invalido_se_rechaza(client: TestClient) -> None:
    assert client.post("/api/leads", json={"email": "no-es-un-correo"}).status_code == 422


def test_origen_desconocido_se_rechaza(client: TestClient) -> None:
    """El origen es una lista cerrada: si fuera texto libre, cada pantalla
    inventaría su etiqueta y el conteo por origen dejaría de servir."""
    resp = client.post("/api/leads", json={"email": "x@ejemplo.cl", "source": "cualquier-cosa"})
    assert resp.status_code == 422


def test_carrera_de_dos_envios_simultaneos_no_devuelve_error(
    client: TestClient, db_session: Session, monkeypatch
) -> None:
    """Dos envíos del mismo correo a la vez leen ambos "no existe" y ambos
    insertan. El índice único evita la fila duplicada; lo que no puede pasar es
    que el segundo se vaya en 500 por algo que para quien lo mandó salió bien.

    La ventana de la carrera se simula dejando ciega a la consulta previa: la
    fila ya está en la base, pero el SELECT devuelve None, que es exactamente
    lo que ve el request perdedor.
    """
    db_session.add(Lead(email="carrera@ejemplo.cl", source="demo"))
    db_session.commit()

    class SinResultado:
        def scalar_one_or_none(self) -> None:
            return None

    execute_real = db_session.execute
    monkeypatch.setattr(db_session, "execute", lambda *a, **k: SinResultado())

    resp = client.post("/api/leads", json={"email": "carrera@ejemplo.cl"})

    monkeypatch.setattr(db_session, "execute", execute_real)
    assert resp.status_code == 201
    assert len(db_session.execute(select(Lead)).scalars().all()) == 1
