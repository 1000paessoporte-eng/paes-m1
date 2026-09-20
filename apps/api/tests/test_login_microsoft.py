"""Inicio de sesión con Microsoft (Entra ID).

Lo que se prueba acá es lo que puede salir mal con las CUENTAS --duplicar a
una persona que ya existía, o perderle el historial-- y no el canje con
Microsoft, que es una llamada a un tercero. El canje se sustituye; lo que se
verifica de él son los casos en que el token vuelve incompleto, que sí son
nuestros.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.users import microsoft, service
from paes_api.modules.users.models import User

CLAIMS = {"sub": "oid-123", "email": "alumna@colegio.cl", "name": "Ana Silva"}


@pytest.fixture()
def identidad_falsa(monkeypatch):
    """Microsoft dice que la persona es quien diga `claims`."""

    def _usar(claims: dict[str, str] = CLAIMS):
        monkeypatch.setattr(microsoft, "identidad", lambda *a, **k: claims)

    _usar()
    return _usar


def _entrar(db: Session) -> User:
    return service.login_with_microsoft(db, "code", "verifier", "https://x/cb", "client-id")


def test_primera_vez_crea_la_cuenta(db_session: Session, identidad_falsa) -> None:
    user = _entrar(db_session)
    assert user.email == "alumna@colegio.cl"
    assert user.microsoft_sub == "oid-123"
    #: Sin contraseña: nunca eligió una, y dejarla en blanco (no vacía) es lo
    #: que impide que alguien entre con "" como clave.
    assert user.hashed_password is None


def test_volver_a_entrar_no_duplica(db_session: Session, identidad_falsa) -> None:
    primero = _entrar(db_session)
    segundo = _entrar(db_session)
    assert primero.id == segundo.id
    assert db_session.execute(select(User)).scalars().all() == [primero]


def test_el_correo_ya_registrado_se_enlaza_y_conserva_su_historial(
    db_session: Session, identidad_falsa
) -> None:
    """Quien se registró con su correo del colegio y contraseña, y meses
    después entra con el botón de Microsoft, es la misma persona. Crear una
    cuenta nueva le escondería todos sus ensayos."""
    ya_estaba = User(
        email="alumna@colegio.cl", name="Ana", hashed_password="hash-de-antes"
    )
    db_session.add(ya_estaba)
    db_session.commit()

    user = _entrar(db_session)
    assert user.id == ya_estaba.id
    assert user.microsoft_sub == "oid-123"
    #: Conserva su contraseña: puede seguir entrando por donde entraba.
    assert user.hashed_password == "hash-de-antes"
    assert len(db_session.execute(select(User)).scalars().all()) == 1


def test_el_mismo_correo_en_google_y_microsoft_es_una_sola_cuenta(
    db_session: Session, identidad_falsa
) -> None:
    con_google = User(
        email="alumna@colegio.cl", name="Ana", hashed_password=None, google_sub="g-1"
    )
    db_session.add(con_google)
    db_session.commit()

    user = _entrar(db_session)
    assert user.id == con_google.id
    assert (user.google_sub, user.microsoft_sub) == ("g-1", "oid-123")


def test_sin_client_id_no_se_intenta_entrar() -> None:
    """Un despliegue sin Microsoft configurado tiene que decirlo, no fallar
    a medio camino contra un tercero."""
    with pytest.raises(microsoft.MicrosoftAuthError, match="no está configurado"):
        microsoft.identidad("code", "verifier", "https://x/cb", "")


def test_un_token_sin_correo_o_sin_identificador_se_rechaza(monkeypatch) -> None:
    monkeypatch.setattr(microsoft, "_canjear", lambda *a, **k: "token")

    monkeypatch.setattr(microsoft, "_verificar", lambda *a, **k: {"oid": "x", "name": "N"})
    with pytest.raises(microsoft.MicrosoftAuthError, match="correo"):
        microsoft.identidad("c", "v", "https://x/cb", "client-id")

    monkeypatch.setattr(
        microsoft, "_verificar", lambda *a, **k: {"preferred_username": "a@b.cl"}
    )
    with pytest.raises(microsoft.MicrosoftAuthError, match="identificador"):
        microsoft.identidad("c", "v", "https://x/cb", "client-id")


def test_el_correo_del_colegio_viene_en_preferred_username(monkeypatch) -> None:
    """Las cuentas de organización no siempre traen `email`: ahí el correo va
    en `preferred_username`, que en Entra es el UPN."""
    monkeypatch.setattr(microsoft, "_canjear", lambda *a, **k: "token")
    monkeypatch.setattr(
        microsoft,
        "_verificar",
        lambda *a, **k: {"oid": "o-9", "preferred_username": "Alumno@Colegio.CL"},
    )
    quien = microsoft.identidad("c", "v", "https://x/cb", "client-id")
    #: El correo se guarda en minúsculas --para que no haya dos cuentas por
    #: cómo lo escribió el colegio-- pero el nombre conserva las mayúsculas:
    #: es lo que se le muestra a la persona.
    assert quien == {"sub": "o-9", "email": "alumno@colegio.cl", "name": "Alumno"}


def test_el_endpoint_responde_401_si_microsoft_rechaza(
    client: TestClient, monkeypatch
) -> None:
    def explota(*a, **k):
        raise microsoft.MicrosoftAuthError("Microsoft rechazó el inicio de sesión")

    monkeypatch.setattr(microsoft, "identidad", explota)
    r = client.post(
        "/api/auth/microsoft",
        json={"code": "c", "code_verifier": "v", "redirect_uri": "https://x/cb"},
    )
    assert r.status_code == 401
    assert "rechazó" in r.json()["detail"]


def test_el_endpoint_abre_sesion_y_deja_el_registro(
    client: TestClient, db_session: Session, monkeypatch
) -> None:
    monkeypatch.setattr(microsoft, "identidad", lambda *a, **k: CLAIMS)
    r = client.post(
        "/api/auth/microsoft",
        json={"code": "c", "code_verifier": "v", "redirect_uri": "https://x/cb"},
    )
    assert r.status_code == 200, r.text
    cuerpo = r.json()
    assert cuerpo["user"]["email"] == "alumna@colegio.cl"
    assert cuerpo["access_token"]

    #: El panel de administración cuenta por dónde entra la gente; si esto no
    #: se registrara, Microsoft sería invisible en esas cifras.
    from paes_api.modules.users.models import LoginEvent

    eventos = db_session.execute(select(LoginEvent)).scalars().all()
    assert [e.method for e in eventos] == ["microsoft"]


def test_la_config_dice_si_microsoft_esta_disponible(client: TestClient) -> None:
    #: Sin MICROSOFT_CLIENT_ID en el entorno de tests, la web no debe ofrecerlo.
    assert client.get("/api/auth/config").json()["microsoft_enabled"] is False
