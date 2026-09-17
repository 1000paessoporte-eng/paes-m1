"""Bienvenida y difusión.

Lo que se prueba no es que el correo salga --eso depende del proveedor-- sino
lo que ninguna prueba manual va a pillar a tiempo: que un fallo del proveedor
no impida registrarse, que la bienvenida no se repita, y que una difusión no
llegue a quien pidió que no le escribieran.
"""

import pytest
from fastapi.testclient import TestClient

from paes_api.core.email import CorreoNoEnviado
from paes_api.modules.correos import service
from paes_api.modules.users.models import User


@pytest.fixture()
def enviados(monkeypatch) -> list[tuple[str, str, str]]:
    """Intercepta los envíos reales y deja el registro de lo que se mandó."""
    registro: list[tuple[str, str, str]] = []

    def _falso(to: str, subject: str, body: str) -> None:
        registro.append((to, subject, body))

    monkeypatch.setattr(service, "send_email", _falso)
    return registro


def _usuario(db_session, email: str, **kwargs) -> User:
    u = User(email=email, name="Camila Prueba", hashed_password="x", **kwargs)
    db_session.add(u)
    db_session.commit()
    return u


# ── Bienvenida ──────────────────────────────────────────────────────────


def test_registrarse_dispara_la_bienvenida(client: TestClient, enviados) -> None:
    respuesta = client.post(
        "/api/auth/register",
        json={"email": "nueva@test.cl", "password": "clave1234", "name": "Camila Soto"},
    )
    assert respuesta.status_code == 201
    assert len(enviados) == 1
    destino, asunto, cuerpo = enviados[0]
    assert destino == "nueva@test.cl"
    assert "Camila" in asunto
    assert "/perfil" in cuerpo  # el pie de baja va siempre


def test_si_el_correo_falla_el_registro_igual_funciona(
    client: TestClient, monkeypatch
) -> None:
    """Un proveedor caído no puede dejar a nadie sin poder crear su cuenta."""

    def _explota(to: str, subject: str, body: str) -> None:
        raise CorreoNoEnviado("proveedor caído")

    monkeypatch.setattr(service, "send_email", _explota)

    respuesta = client.post(
        "/api/auth/register",
        json={"email": "pese@test.cl", "password": "clave1234", "name": "Diego Ruiz"},
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["access_token"]


def test_la_bienvenida_no_se_repite_al_iniciar_sesion(
    client: TestClient, enviados
) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "vuelve@test.cl", "password": "clave1234", "name": "Ana Díaz"},
    )
    client.post(
        "/api/auth/login", json={"email": "vuelve@test.cl", "password": "clave1234"}
    )
    assert len(enviados) == 1


# ── Difusión ────────────────────────────────────────────────────────────


def test_no_se_difunde_a_quien_apago_los_avisos(db_session, enviados) -> None:
    _usuario(db_session, "apagado@test.cl", recordatorios_email=False)
    _usuario(db_session, "activo@test.cl")

    resultado = service.difundir(db_session, "Novedades", "Hola", pausa=0)

    assert resultado["enviados"] == 1
    assert [d for d, _, _ in enviados] == ["activo@test.cl"]


def test_el_publico_separa_correo_de_google(db_session) -> None:
    _usuario(db_session, "conclave@test.cl")
    u = User(email="congoogle@test.cl", name="G", hashed_password=None, google_sub="123")
    db_session.add(u)
    db_session.commit()

    assert [x.email for x in service.destinatarios(db_session, "correo")] == [
        "conclave@test.cl"
    ]
    assert [x.email for x in service.destinatarios(db_session, "google")] == [
        "congoogle@test.cl"
    ]
    assert len(service.destinatarios(db_session, "todos")) == 2


def test_modo_prueba_no_manda_nada(db_session, enviados) -> None:
    """La difusión no se puede deshacer: el ensayo tiene que ser inofensivo."""
    _usuario(db_session, "alguien@test.cl")

    resultado = service.difundir(db_session, "Novedades", "Hola", prueba=True)

    assert resultado["enviados"] == 0
    assert resultado["destinatarios"] == ["alguien@test.cl"]
    assert enviados == []


def test_una_direccion_rebotada_no_corta_la_tanda(db_session, monkeypatch) -> None:
    ok: list[str] = []

    def _falla_la_primera(to: str, subject: str, body: str) -> None:
        if to == "rebota@test.cl":
            raise CorreoNoEnviado("dirección inexistente")
        ok.append(to)

    monkeypatch.setattr(service, "send_email", _falla_la_primera)
    _usuario(db_session, "rebota@test.cl")
    _usuario(db_session, "llega@test.cl")

    resultado = service.difundir(db_session, "Novedades", "Hola", pausa=0)

    assert resultado == {
        "enviados": 1,
        "fallidos": 1,
        "destinatarios": ["rebota@test.cl", "llega@test.cl"],
        "prueba": False,
    }
    assert ok == ["llega@test.cl"]


def test_publico_desconocido_es_error(db_session) -> None:
    with pytest.raises(ValueError):
        service.destinatarios(db_session, "inventado")
