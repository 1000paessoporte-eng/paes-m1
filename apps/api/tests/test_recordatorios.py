"""Recordatorios por correo.

Lo que se prueba acá no es que el correo salga —eso depende del proveedor— sino
las tres reglas que evitan que este sistema se convierta en spam.
"""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from paes_api.modules.exam_focus.models import ExamAttempt
from paes_api.modules.reminders import service
from paes_api.modules.users.models import User


def _usuario(db_session, email: str, **kwargs) -> User:
    u = User(email=email, name="Camila Prueba", hashed_password="x", **kwargs)
    db_session.add(u)
    db_session.commit()
    return u


def test_no_se_le_escribe_a_quien_los_apago(db_session) -> None:
    _usuario(db_session, "apagado@test.cl", recordatorios_email=False)
    resultado = service.enviar_recordatorios(db_session)
    assert resultado["enviados"] == 0


def test_no_se_escribe_dos_dias_seguidos(db_session) -> None:
    """Un recordatorio diario deja de ser recordatorio y pasa a ser acoso; a la
    tercera vez la cuenta marca el remitente como spam y se pierde el dominio
    para todos los correos, incluidos los de recuperar contraseña."""
    _usuario(
        db_session,
        "ayer@test.cl",
        ultimo_recordatorio=datetime.now(UTC) - timedelta(hours=20),
    )
    assert service.enviar_recordatorios(db_session)["enviados"] == 0


def test_no_se_le_escribe_a_quien_ya_rindio_hoy(db_session) -> None:
    u = _usuario(db_session, "hoy@test.cl")
    ahora = datetime.now(UTC)
    db_session.add(
        ExamAttempt(
            user_id=u.id, subject="m1", status="submitted", estimated_score=500,
            started_at=ahora, finished_at=ahora, duration_limit_seconds=2580,
        )
    )
    db_session.commit()
    assert service.enviar_recordatorios(db_session)["enviados"] == 0


def test_se_le_escribe_a_quien_lleva_dias_sin_rendir(db_session) -> None:
    u = _usuario(db_session, "pendiente@test.cl")
    hace_tres = datetime.now(UTC) - timedelta(days=3)
    db_session.add(
        ExamAttempt(
            user_id=u.id, subject="m1", status="submitted", estimated_score=500,
            started_at=hace_tres, finished_at=hace_tres, duration_limit_seconds=2580,
        )
    )
    db_session.commit()

    assert service.enviar_recordatorios(db_session)["enviados"] == 1
    # Y queda registrado, para que el próximo intento respete el descanso.
    assert db_session.get(User, u.id).ultimo_recordatorio is not None


def test_el_endpoint_del_cron_esta_cerrado_sin_secreto(client: TestClient) -> None:
    """Un disparador de correos masivos accesible por internet es la clase de
    puerta que no se deja entornada por comodidad."""
    assert client.post("/api/reminders/run").status_code == 404
