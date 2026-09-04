"""Las defensas que se pueden romper sin que nadie se dé cuenta.

Un fallo de seguridad no rompe ningún test por sí solo: el sitio sigue
funcionando igual de bien con la puerta abierta que con la puerta cerrada. Por
eso estas comprobaciones existen — para que quitar una defensa cueste un test
en rojo y no pase inadvertido en una revisión.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.orm import Session
from test_practice import _make_node_with_question

from paes_api.core.config import Settings
from paes_api.core.security import create_access_token, decode_access_token


class TestClaveDeFirma:
    """La clave por defecto no puede llegar a producción.

    Quien la conozca —y está escrita en el repo, que es público— puede firmar
    un token de cualquier usuario, incluido uno con is_admin.
    """

    def test_la_clave_por_defecto_no_arranca_en_produccion(self) -> None:
        with pytest.raises(ValidationError, match="SECRET_KEY"):
            Settings(environment="production", secret_key="change-me")

    def test_una_clave_corta_avisa_pero_no_tumba_el_sitio(self) -> None:
        """Corta no es lo mismo que publica.

        La de por defecto la conoce cualquiera que lea el repo; una corta y
        propia solo es mas debil. Y como en Vercel esta variable no se puede
        volver a leer, cortar el arranque por longitud podria dejar el sitio
        caido para arreglar algo que no estaba roto.
        """
        with pytest.warns(UserWarning, match="SECRET_KEY"):
            s = Settings(environment="production", secret_key="corta")
        assert s.secret_key == "corta"

    def test_una_clave_de_verdad_si(self) -> None:
        s = Settings(environment="production", secret_key="x" * 64)
        assert s.environment == "production"

    def test_en_desarrollo_no_estorba(self) -> None:
        """El validador no puede volver incómodo el trabajo local."""
        s = Settings(environment="development", secret_key="change-me")
        assert s.secret_key == "change-me"


class TestToken:
    def test_un_token_con_otra_firma_no_vale(self) -> None:
        """El caso que importa: un token bien formado pero firmado con otra
        clave. Si esto pasara, cualquiera entraría como cualquiera."""
        ajeno = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxIiwiZXhwIjo0MTAyNDQ0ODAwfQ."
            "firma-inventada-que-no-corresponde"
        )
        assert decode_access_token(ajeno) is None

    def test_basura_no_revienta(self) -> None:
        assert decode_access_token("no-es-un-token") is None
        assert decode_access_token("") is None

    def test_el_nuestro_si_vale(self) -> None:
        assert decode_access_token(create_access_token(7)) == 7


class TestAutorizacion:
    """Que un usuario no pueda leer lo de otro. Es el fallo más común y el más
    caro: se llega con solo cambiar un número en la URL."""

    def test_no_se_puede_ver_el_intento_de_otro(
        self, client: TestClient, db_session: Session, register_user
    ) -> None:
        # Sin preguntas en el banco no se puede armar un ensayo, y el test
        # moriria por 409 antes de llegar a comprobar lo que importa.
        _make_node_with_question(db_session, "seguridad_idor")
        propias, _ = register_user(email="duena-del-intento@milpaes.cl")
        ajenas, _ = register_user(email="curiosa@milpaes.cl")

        creado = client.post(
            "/api/exam/start",
            json={"subject": "m1", "question_count": 5, "pace": "oficial", "axes": []},
            headers=propias,
        )
        assert creado.status_code == 200, creado.text
        attempt_id = creado.json()["attempt_id"]

        # Y ahora otra cuenta pide ese mismo intento.
        robo = client.get(f"/api/exam/{attempt_id}", headers=ajenas)
        # 404 y no 403: no debe ni confirmar que el intento existe.
        assert robo.status_code == 404, (
            f"una cuenta ajena pudo ver el intento {attempt_id}: {robo.status_code}"
        )

    def test_el_panel_de_admin_no_se_abre_con_una_cuenta_normal(
        self, client: TestClient, register_user
    ) -> None:
        normales, _ = register_user(email="alumna-cualquiera@milpaes.cl")
        r = client.get("/api/admin/metrics", headers=normales)
        assert r.status_code == 404, f"esperaba 404, vino {r.status_code}"

    def test_sin_sesion_no_se_entra(self, client: TestClient) -> None:
        assert client.get("/api/admin/metrics").status_code == 401
        assert client.get("/api/exam/repaso").status_code == 401
