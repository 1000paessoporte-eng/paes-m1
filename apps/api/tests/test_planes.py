"""Planes, límites y códigos promocionales."""

import pytest
from fastapi.testclient import TestClient

from paes_api.modules.billing import service
from paes_api.modules.billing.models import Plan, PromoCode


def test_sin_suscripcion_el_plan_es_gratis(client: TestClient, register_user) -> None:
    headers, _ = register_user()
    datos = client.get("/api/plan", headers=headers).json()
    assert datos["plan"] == "gratis"
    assert datos["ensayos_limite"] == 4
    assert datos["carreras_limite"] == 1
    assert "analisis_avanzado" not in datos, "un limite que nadie aplica no se informa"


def test_un_codigo_valido_deja_el_plan_pro(
    client: TestClient, register_user, db_session
) -> None:
    db_session.add(PromoCode(codigo="SALA-4B", plan=Plan.PRO, dias=60, usos_maximos=10))
    db_session.commit()

    headers, _ = register_user(email="canje@test.cl")
    resp = client.post("/api/plan/canjear", headers=headers, json={"codigo": "sala-4b"})
    assert resp.status_code == 200, resp.text
    datos = resp.json()
    assert datos["plan"] == "pro"
    assert datos["ensayos_limite"] is None
    assert datos["carreras_limite"] == 10


def test_el_mismo_codigo_no_se_canjea_dos_veces(
    client: TestClient, register_user, db_session
) -> None:
    """Sin esto, un solo código es plan gratis infinito."""
    db_session.add(PromoCode(codigo="REPE", plan=Plan.PRO, dias=30, usos_maximos=99))
    db_session.commit()

    headers, _ = register_user(email="repe@test.cl")
    assert client.post("/api/plan/canjear", headers=headers, json={"codigo": "REPE"}).status_code == 200
    segunda = client.post("/api/plan/canjear", headers=headers, json={"codigo": "REPE"})
    assert segunda.status_code == 400
    assert "canjeaste" in segunda.json()["detail"]


def test_un_codigo_agotado_se_rechaza(
    client: TestClient, register_user, db_session
) -> None:
    db_session.add(
        PromoCode(codigo="AGOTADO", plan=Plan.PRO, dias=30, usos_maximos=1, usos=1)
    )
    db_session.commit()
    headers, _ = register_user(email="agotado@test.cl")
    resp = client.post("/api/plan/canjear", headers=headers, json={"codigo": "AGOTADO"})
    assert resp.status_code == 400
    assert "agotó" in resp.json()["detail"]


def test_un_codigo_vencido_se_rechaza(
    client: TestClient, register_user, db_session
) -> None:
    from datetime import UTC, datetime, timedelta

    db_session.add(
        PromoCode(
            codigo="VENCIDO", plan=Plan.PRO, dias=30, usos_maximos=5,
            vence_el=datetime.now(UTC) - timedelta(days=1),
        )
    )
    db_session.commit()
    headers, _ = register_user(email="vencido@test.cl")
    resp = client.post("/api/plan/canjear", headers=headers, json={"codigo": "VENCIDO"})
    assert resp.status_code == 400
    assert "venció" in resp.json()["detail"]


def test_una_suscripcion_vencida_no_da_plan(
    client: TestClient, register_user, db_session
) -> None:
    from datetime import UTC, datetime, timedelta

    from paes_api.modules.billing.models import Subscription

    headers, usuario = register_user(email="expirado@test.cl")
    db_session.add(
        Subscription(
            user_id=usuario["id"], plan=Plan.PRO,
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
    )
    db_session.commit()

    assert client.get("/api/plan", headers=headers).json()["plan"] == "gratis"


@pytest.mark.parametrize("plan", list(Plan))
def test_todo_plan_declara_sus_limites(plan: Plan) -> None:
    """Un plan sin límites declarados haría que `limites_de(plan)` reviente en
    producción la primera vez que alguien lo tenga."""
    assert service.limites_de(plan) is not None


def test_los_limites_no_bloquean_todavia() -> None:
    """Mientras el plan Pro no se pueda contratar, el tope se informa pero no
    corta: mandar a alguien a una pantalla que dice "disponible pronto" es
    frustración sin salida."""
    assert service.limites_activos() is False


def test_cancelar_apaga_la_renovacion_sin_quitar_lo_pagado(
    client: TestClient, db_session, register_user
) -> None:
    """Cancelar no es cortar el acceso: el período pagado se respeta entero.
    Cortarlo el día que cancela sería cobrarle días que no puede usar."""
    from datetime import UTC, datetime, timedelta

    from paes_api.modules.billing.models import (
        Origen,
        Plan,
        Subscription,
        SubscriptionStatus,
    )
    from paes_api.modules.users.models import User
    from sqlalchemy import select

    headers, _ = register_user(email="cancela@milpaes.cl")
    user = db_session.execute(select(User).where(User.email == "cancela@milpaes.cl")).scalar_one()
    vence = datetime.now(UTC) + timedelta(days=20)
    db_session.add(
        Subscription(
            user_id=user.id, plan=Plan.PRO, status=SubscriptionStatus.ACTIVE,
            origen=Origen.PAGO, expires_at=vence,
        )
    )
    db_session.commit()

    resp = client.post("/api/plan/cancelar", headers=headers)
    assert resp.status_code == 200

    sub = db_session.execute(select(Subscription)).scalar_one()
    # Lo que se apaga es la RENOVACIÓN, y la suscripción sigue vigente hasta su
    # fecha. Este test comprobaba `status == CANCELED` y pasaba en verde
    # mientras el usuario perdía el acceso en el acto: `plan_actual` solo mira
    # las ACTIVE. Comprobar el estado interno no servía de nada; lo que hay que
    # comprobar es que la persona siga entrando.
    assert sub.cancelada_al_terminar is True
    assert sub.status == SubscriptionStatus.ACTIVE
    assert client.get("/api/plan", headers=headers).json()["plan"] == "pro"
    # SQLite no guarda la zona horaria, así que se comparan los instantes.
    assert sub.expires_at.replace(tzinfo=UTC) == vence, "la fecha de término no se toca"


def test_cancelar_sin_suscripcion_no_finge(client: TestClient, register_user) -> None:
    headers, _ = register_user(email="sinplan@milpaes.cl")
    assert client.post("/api/plan/cancelar", headers=headers).status_code == 409
