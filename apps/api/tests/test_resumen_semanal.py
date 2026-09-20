"""Resumen semanal de progreso y el reparto de un correo al día como máximo."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from paes_api.modules.exam_focus.models import ExamAttempt
from paes_api.modules.practice.models import PracticeAnswer
from paes_api.modules.reminders import resumen, service
from paes_api.modules.users.models import User

#: Un domingo y un sábado fijos: el día de la semana decide qué correo sale.
DOMINGO = datetime(2026, 9, 20, 21, tzinfo=UTC)
SABADO = datetime(2026, 9, 19, 20, tzinfo=UTC)


def _usuario(db_session, email: str, **kwargs) -> User:
    kwargs.setdefault("created_at", DOMINGO - timedelta(days=60))
    u = User(email=email, name="Camila Prueba", hashed_password="x", **kwargs)
    db_session.add(u)
    db_session.commit()
    return u


def _ensayo(db_session, user: User, cuando: datetime, puntaje: int) -> None:
    db_session.add(
        ExamAttempt(
            user_id=user.id, subject="m1", status="submitted", estimated_score=puntaje,
            started_at=cuando, finished_at=cuando, duration_limit_seconds=2580,
        )
    )
    db_session.commit()


def _enviados(monkeypatch) -> list[tuple[str, ...]]:
    """(destino, asunto, cuerpo, html). El html es la versión con diseño."""
    salida: list[tuple[str, ...]] = []
    monkeypatch.setattr(resumen, "send_email", lambda *a: salida.append(a))
    monkeypatch.setattr(service, "send_email", lambda *a: salida.append(a))
    return salida


def test_el_domingo_no_sale_recordatorio(db_session, monkeypatch) -> None:
    """El domingo el único correo es el resumen: nunca dos el mismo día."""
    u = _usuario(db_session, "domingo@test.cl")
    _ensayo(db_session, u, DOMINGO - timedelta(days=3), 500)
    salida = _enviados(monkeypatch)

    assert service.enviar_recordatorios(db_session, ahora=DOMINGO)["enviados"] == 0
    assert service.enviar_recordatorios(db_session, ahora=SABADO)["enviados"] == 1
    assert len(salida) == 1


def test_el_recordatorio_dice_cuantos_dias_quedan(db_session, monkeypatch) -> None:
    u = _usuario(db_session, "dias@test.cl")
    _ensayo(db_session, u, SABADO - timedelta(days=3), 500)
    salida = _enviados(monkeypatch)

    service.enviar_recordatorios(db_session, ahora=SABADO)
    _, _, cuerpo, _html = salida[0]
    assert "días para la PAES" in cuerpo
    assert "/perfil" in cuerpo  # la baja, siempre


def test_resumen_con_actividad_compara_con_la_semana_pasada(db_session, monkeypatch) -> None:
    u = _usuario(db_session, "activa@test.cl")
    _ensayo(db_session, u, DOMINGO - timedelta(days=20), 480)
    _ensayo(db_session, u, DOMINGO - timedelta(days=2), 560)
    for i in range(10):
        db_session.add(PracticeAnswer(
            user_id=u.id, question_id=1, skill_node_id=1, is_correct=i < 7,
            answered_at=DOMINGO - timedelta(days=1),
        ))
    db_session.commit()
    salida = _enviados(monkeypatch)

    assert resumen.enviar_resumenes(db_session, ahora=DOMINGO)["enviados"] == 1
    _, asunto, cuerpo, html = salida[0]
    assert "10 preguntas" in asunto and "70%" in asunto
    assert "nuevo récord" in cuerpo and "560" in cuerpo and "480" in cuerpo
    assert "/analitica" in cuerpo and "/perfil" in cuerpo
    # Y la versión con diseño cuenta lo mismo.
    assert "70%" in html and "560" in html and "/perfil#correos" in html


def test_resumen_sin_actividad_reciente_no_sale(db_session, monkeypatch) -> None:
    """A quien no tocó la plataforma en cuatro semanas no se le resume nada."""
    u = _usuario(db_session, "dormida@test.cl")
    _ensayo(db_session, u, DOMINGO - timedelta(days=40), 500)
    salida = _enviados(monkeypatch)

    assert resumen.enviar_resumenes(db_session, ahora=DOMINGO)["enviados"] == 0
    assert salida == []


def test_resumen_de_semana_floja_no_reprocha(db_session, monkeypatch) -> None:
    u = _usuario(db_session, "floja@test.cl")
    _ensayo(db_session, u, DOMINGO - timedelta(days=10), 500)
    salida = _enviados(monkeypatch)

    assert resumen.enviar_resumenes(db_session, ahora=DOMINGO)["enviados"] == 1
    _, asunto, _, _ = salida[0]
    assert "no alcanzaste" in asunto


def test_resumen_respeta_el_opt_out(db_session, monkeypatch) -> None:
    u = _usuario(db_session, "apagado@test.cl", recordatorios_email=False)
    _ensayo(db_session, u, DOMINGO - timedelta(days=1), 500)
    assert resumen.enviar_resumenes(db_session, ahora=DOMINGO)["enviados"] == 0


def test_el_cron_del_resumen_esta_cerrado_sin_secreto(client: TestClient) -> None:
    assert client.get("/api/reminders/resumen").status_code == 404
