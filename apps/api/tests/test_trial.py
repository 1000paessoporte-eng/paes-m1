"""La prueba gratis de 3 días y el cobro recurrente con Flow.

Lo que se prueba acá es que la frase que va en pantalla —"3 días gratis,
después $9.990 al mes, cancelas cuando quieras"— sea verdad en las tres
partes. No es una prueba de que Flow funcione: es una prueba de que no
prometemos un cobro que el sistema no hace, ni cortamos un acceso que el
sistema ya cobró.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.core.config import get_settings
from paes_api.modules.billing import service
from paes_api.modules.billing.models import (
    FlowCustomer,
    Origen,
    Plan,
    Subscription,
    SubscriptionStatus,
)
from paes_api.modules.users.models import User


def _usuario(db: Session, email: str) -> User:
    return db.execute(select(User).where(User.email == email)).scalar_one()


@pytest.fixture()
def flow_configurado(monkeypatch):
    """Deja el cobro recurrente encendido para el test.

    Las credenciales son de mentira a propósito: nada de lo que sigue habla con
    Flow de verdad, todo va parcheado. Lo único que importa es que
    `trial_disponible()` diga que sí.
    """
    get_settings.cache_clear()
    monkeypatch.setenv("FLOW_API_KEY", "llave-de-prueba")
    monkeypatch.setenv("FLOW_SECRET_KEY", "secreto-de-prueba")
    monkeypatch.setenv("FLOW_PLAN_PRO_ID", "pro-mensual-v1")
    monkeypatch.setenv("TRIAL_DIAS", "3")
    yield
    for var in ("FLOW_API_KEY", "FLOW_SECRET_KEY", "FLOW_PLAN_PRO_ID", "TRIAL_DIAS"):
        monkeypatch.delenv(var, raising=False)
    get_settings.cache_clear()


def _fecha_flow(cuando: datetime) -> str:
    return cuando.strftime("%Y-%m-%d %H:%M:%S")


def _suscripcion_flow(*, fin: datetime, fin_trial: datetime | None = None) -> dict:
    datos = {"subscriptionId": "sub-1", "period_end": _fecha_flow(fin)}
    if fin_trial is not None:
        datos["trial_end"] = _fecha_flow(fin_trial)
    return datos


def _tomar_el_trial(client: TestClient, headers: dict, *, dias: int = 3) -> None:
    """Recorre el camino completo: inscribir tarjeta y volver de Flow."""
    ahora = datetime.now(UTC)
    fin = ahora + timedelta(days=dias)
    with (
        patch(
            "paes_api.modules.billing.flow.cliente_crear",
            return_value={"customerId": "cus-1"},
        ),
        patch(
            "paes_api.modules.billing.flow.cliente_registrar",
            return_value={"url": "https://flow.test/registro", "token": "tok-reg"},
        ),
    ):
        resp = client.post("/api/plan/trial", headers=headers)
    assert resp.status_code == 200, resp.text

    with (
        patch(
            "paes_api.modules.billing.flow.cliente_estado_registro",
            return_value={
                "status": "1",
                "creditCardType": "Visa",
                "last4CardDigits": "4242",
            },
        ),
        patch(
            "paes_api.modules.billing.flow.suscripcion_crear",
            return_value=_suscripcion_flow(fin=fin, fin_trial=fin),
        ),
    ):
        vuelta = client.post(
            "/api/plan/trial/retorno",
            data={"token": "tok-reg"},
            follow_redirects=False,
        )
    assert vuelta.status_code == 303


# ---------------------------------------------------------------------------
# Que no se ofrezca lo que no se puede cumplir
# ---------------------------------------------------------------------------


def test_sin_plan_en_flow_no_se_ofrece_la_prueba(
    client: TestClient, register_user
) -> None:
    """Anunciar 3 días gratis sin el plan recurrente creado sería mandar a la
    persona a un error DESPUÉS de haber entregado su tarjeta."""
    headers, _ = register_user(email="sinflow@milpaes.cl")
    datos = client.get("/api/plan", headers=headers).json()
    assert datos["trial_disponible"] is False

    assert client.post("/api/plan/trial", headers=headers).status_code == 503


def test_productos_informa_cuanto_se_cobra_despues_de_la_prueba(
    client: TestClient, flow_configurado
) -> None:
    """Un trial que no dice qué se cobra después es una suscripción a ciegas.

    El monto sale del producto mensual y no de una constante aparte: si el
    precio sube en un solo lugar, sube en los dos."""
    body = client.get("/api/plan/productos").json()
    assert body["trial_disponible"] is True
    assert body["trial_dias"] == 3
    assert body["trial_monto"] == service.PRODUCTOS["pro_mensual"].monto


def test_el_trial_requiere_sesion(client: TestClient) -> None:
    assert client.post("/api/plan/trial").status_code == 401


# ---------------------------------------------------------------------------
# La activación
# ---------------------------------------------------------------------------


def test_iniciar_la_prueba_no_activa_nada_por_si_solo(
    client: TestClient, register_user, flow_configurado
) -> None:
    """Si pedir la URL activara el plan, tomarlo sin dejar tarjeta sería
    cuestión de llamar a este endpoint y cerrar la pestaña."""
    headers, _ = register_user(email="apura@milpaes.cl")

    with (
        patch(
            "paes_api.modules.billing.flow.cliente_crear",
            return_value={"customerId": "cus-9"},
        ),
        patch(
            "paes_api.modules.billing.flow.cliente_registrar",
            return_value={"url": "https://flow.test/registro", "token": "tok-9"},
        ),
    ):
        resp = client.post("/api/plan/trial", headers=headers)

    assert resp.status_code == 200
    assert resp.json()["url"] == "https://flow.test/registro?token=tok-9"
    assert client.get("/api/plan", headers=headers).json()["plan"] == "gratis"


def test_la_prueba_se_activa_cuando_flow_confirma_la_tarjeta(
    client: TestClient, register_user, db_session, flow_configurado
) -> None:
    headers, _ = register_user(email="prueba@milpaes.cl")
    _tomar_el_trial(client, headers)

    datos = client.get("/api/plan", headers=headers).json()
    assert datos["plan"] == "pro"
    assert datos["en_trial"] is True
    assert datos["ensayos_limite"] is None
    assert datos["tarjeta"] == "Visa ····4242"

    sub = db_session.execute(select(Subscription)).scalar_one()
    assert sub.origen is Origen.TRIAL, "el trial no es un pago: no se cobró nada"
    assert sub.flow_subscription_id == "sub-1"


def test_si_la_tarjeta_no_queda_inscrita_no_se_activa_nada(
    client: TestClient, register_user, db_session, flow_configurado
) -> None:
    """Quien abandona el formulario de Flow no se lleva el plan Pro."""
    headers, _ = register_user(email="abandona@milpaes.cl")

    with (
        patch(
            "paes_api.modules.billing.flow.cliente_crear",
            return_value={"customerId": "cus-2"},
        ),
        patch(
            "paes_api.modules.billing.flow.cliente_registrar",
            return_value={"url": "https://flow.test/registro", "token": "tok-2"},
        ),
    ):
        client.post("/api/plan/trial", headers=headers)

    with patch(
        "paes_api.modules.billing.flow.cliente_estado_registro",
        return_value={"status": "0"},
    ):
        vuelta = client.post(
            "/api/plan/trial/retorno",
            data={"token": "tok-2"},
            follow_redirects=False,
        )

    # No se le muestra un error crudo: se le manda a la pantalla que consulta
    # el plan real.
    assert vuelta.status_code == 303
    assert "sin-tarjeta" in vuelta.headers["location"]
    assert client.get("/api/plan", headers=headers).json()["plan"] == "gratis"
    assert db_session.execute(select(Subscription)).first() is None


def test_volver_dos_veces_no_crea_dos_suscripciones(
    client: TestClient, register_user, db_session, flow_configurado
) -> None:
    """Recargar la pantalla de vuelta no puede terminar en dos cobros."""
    headers, _ = register_user(email="recarga@milpaes.cl")
    _tomar_el_trial(client, headers)

    with patch(
        "paes_api.modules.billing.flow.suscripcion_crear"
    ) as crear_de_nuevo:
        client.post(
            "/api/plan/trial/retorno",
            data={"token": "tok-reg"},
            follow_redirects=False,
        )

    crear_de_nuevo.assert_not_called()
    assert len(db_session.execute(select(Subscription)).scalars().all()) == 1


def test_la_prueba_es_una_por_cuenta(
    client: TestClient, register_user, db_session, flow_configurado
) -> None:
    """Sin esto, cancelar y volver a suscribirse es Pro gratis para siempre en
    tandas de tres días."""
    headers, _ = register_user(email="viva@milpaes.cl")
    _tomar_el_trial(client, headers)

    # Se vence el trial a mano, para llegar al caso real: alguien que ya la usó
    # y vuelve meses después.
    sub = db_session.execute(select(Subscription)).scalar_one()
    sub.expires_at = datetime.now(UTC) - timedelta(days=90)
    sub.status = SubscriptionStatus.EXPIRED
    db_session.commit()

    assert client.get("/api/plan", headers=headers).json()["trial_disponible"] is False
    resp = client.post("/api/plan/trial", headers=headers)
    assert resp.status_code == 409
    assert "una por cuenta" in resp.json()["detail"]


def test_el_retorno_sin_token_no_revienta(
    client: TestClient, flow_configurado
) -> None:
    """Alguien que escribe la URL a mano no puede recibir un 500."""
    vuelta = client.post("/api/plan/trial/retorno", follow_redirects=False)
    assert vuelta.status_code == 303
    assert "sin-token" in vuelta.headers["location"]


# ---------------------------------------------------------------------------
# "Cancelas cuando quieras"
# ---------------------------------------------------------------------------


def test_cancelar_conserva_el_acceso_hasta_la_fecha_pagada(
    client: TestClient, register_user, db_session, flow_configurado
) -> None:
    """Este es el bug que la pantalla iba a anunciar como característica.

    `cancelar_suscripcion` ponía `status = CANCELED` y `plan_actual` solo mira
    las ACTIVE, así que el plan volvía a Gratis en el acto: se le cobraba a
    alguien un mes y se le quitaba el día que decía "no quiero renovar". Ahora
    se apaga la renovación y el período corre entero."""
    headers, _ = register_user(email="chao@milpaes.cl")
    user = _usuario(db_session, "chao@milpaes.cl")
    vence = datetime.now(UTC) + timedelta(days=20)
    db_session.add(
        Subscription(
            user_id=user.id,
            plan=Plan.PRO,
            status=SubscriptionStatus.ACTIVE,
            origen=Origen.PAGO,
            expires_at=vence,
        )
    )
    db_session.commit()

    resp = client.post("/api/plan/cancelar", headers=headers)
    assert resp.status_code == 200

    datos = client.get("/api/plan", headers=headers).json()
    assert datos["plan"] == "pro", "pagó 20 días más: no se le quitan"
    assert datos["cancelada_al_terminar"] is True

    sub = db_session.execute(select(Subscription)).scalar_one()
    assert sub.expires_at.replace(tzinfo=UTC) == vence, "la fecha no se toca"


def test_cancelar_apaga_tambien_el_cobro_en_flow(
    client: TestClient, register_user, db_session, flow_configurado
) -> None:
    """Apagarlo solo de este lado sería seguir cobrándole todos los meses a
    alguien que en su pantalla ve "cancelada"."""
    headers, _ = register_user(email="chaoflow@milpaes.cl")
    _tomar_el_trial(client, headers)

    with patch(
        "paes_api.modules.billing.flow.suscripcion_cancelar", return_value={}
    ) as cancelar:
        assert client.post("/api/plan/cancelar", headers=headers).status_code == 200

    cancelar.assert_called_once()
    assert cancelar.call_args.args[0] == "sub-1"
    assert cancelar.call_args.kwargs["al_terminar"] is True, (
        "sin at_period_end Flow corta el mes ya cobrado"
    )


def test_una_vez_vencido_el_trial_el_plan_vuelve_a_gratis(
    client: TestClient, register_user, db_session, flow_configurado
) -> None:
    headers, _ = register_user(email="vencio@milpaes.cl")
    _tomar_el_trial(client, headers)

    sub = db_session.execute(select(Subscription)).scalar_one()
    sub.expires_at = datetime.now(UTC) - timedelta(hours=1)
    db_session.commit()

    # Flow confirma que no hubo cobro: el período terminó donde decía.
    with patch(
        "paes_api.modules.billing.flow.suscripcion_estado",
        return_value=_suscripcion_flow(fin=datetime.now(UTC) - timedelta(hours=1)),
    ):
        datos = client.get("/api/plan", headers=headers).json()

    assert datos["plan"] == "gratis"


# ---------------------------------------------------------------------------
# La reconciliación: quién sabe hasta cuándo está pagado
# ---------------------------------------------------------------------------


def test_el_cobro_del_mes_extiende_el_acceso_sin_aritmetica_propia(
    client: TestClient, register_user, db_session, flow_configurado
) -> None:
    """Cuando Flow cobra el primer mes, la fecha nueva la dice Flow.

    Este servicio no suma 30 días por su cuenta: le pregunta a quien cobró."""
    headers, _ = register_user(email="renueva@milpaes.cl")
    _tomar_el_trial(client, headers)

    sub = db_session.execute(select(Subscription)).scalar_one()
    sub.expires_at = datetime.now(UTC) - timedelta(minutes=5)
    db_session.commit()

    nuevo_fin = datetime.now(UTC) + timedelta(days=30)
    with patch(
        "paes_api.modules.billing.flow.suscripcion_estado",
        return_value=_suscripcion_flow(fin=nuevo_fin),
    ):
        datos = client.get("/api/plan", headers=headers).json()

    assert datos["plan"] == "pro"
    assert datos["en_trial"] is False, "ya no es prueba: se cobró"
    db_session.refresh(sub)
    assert sub.expires_at.replace(tzinfo=UTC).date() == nuevo_fin.date()


def test_si_flow_no_responde_no_se_le_corta_el_acceso_a_quien_pago(
    client: TestClient, register_user, db_session, flow_configurado
) -> None:
    """Una caída de Flow no puede dejar afuera a alguien que está al día.

    Regalar unas horas hasta que Flow vuelva a responder es mucho más barato
    —y mucho menos injusto— que cerrarle la puerta a quien pagó."""
    from paes_api.modules.billing import flow

    headers, _ = register_user(email="caida@milpaes.cl")
    _tomar_el_trial(client, headers)

    sub = db_session.execute(select(Subscription)).scalar_one()
    sub.expires_at = datetime.now(UTC) - timedelta(minutes=5)
    db_session.commit()

    with patch(
        "paes_api.modules.billing.flow.suscripcion_estado",
        side_effect=flow.FlowError("Flow no contesta"),
    ):
        datos = client.get("/api/plan", headers=headers).json()

    assert datos["plan"] == "pro"
    db_session.refresh(sub)
    assert sub.status is SubscriptionStatus.ACTIVE, "no se da por vencida a ciegas"


def test_el_barrido_necesita_el_secreto(client: TestClient, monkeypatch) -> None:
    """Sin secreto configurado queda cerrado, no abierto: es una tarea que
    habla con la pasarela de pago."""
    assert client.get("/api/plan/flow/reconciliar").status_code == 404

    get_settings.cache_clear()
    monkeypatch.setenv("CRON_SECRET", "abc123")
    try:
        assert client.get("/api/plan/flow/reconciliar").status_code == 401
        resp = client.get(
            "/api/plan/flow/reconciliar", headers={"Authorization": "Bearer abc123"}
        )
        assert resp.status_code == 200
        assert resp.json() == {"revisadas": 0}
    finally:
        monkeypatch.delenv("CRON_SECRET", raising=False)
        get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Borrar la cuenta
# ---------------------------------------------------------------------------


def test_borrar_la_cuenta_apaga_el_cobro_recurrente(
    client: TestClient, register_user, db_session, flow_configurado
) -> None:
    """Una suscripción viva en Flow sobrevive al borrado de la cuenta y sigue
    cobrando a una tarjeta cuyo dueño ya no tiene dónde reclamar."""
    headers, _ = register_user(email="mevoy@milpaes.cl")
    _tomar_el_trial(client, headers)

    with patch(
        "paes_api.modules.billing.flow.suscripcion_cancelar", return_value={}
    ) as cancelar:
        resp = client.request(
            "DELETE", "/api/auth/me", headers=headers, json={"password": "clave1234"}
        )

    assert resp.status_code in (200, 204), resp.text
    cancelar.assert_called_once()
    assert db_session.execute(select(FlowCustomer)).first() is None


def test_el_barrido_no_vence_lo_que_flow_no_pudo_confirmar(
    db_session, register_user, client: TestClient, flow_configurado
) -> None:
    """Misma política que `plan_actual`: cuando no se sabe, no se corta.

    Si el barrido diera por vencida una suscripción solo porque la consulta
    falló, una caída de Flow a las 8:30 de la mañana dejaría sin plan a todos
    los que estén al día."""
    from paes_api.modules.billing import flow

    headers, _ = register_user(email="barrido@milpaes.cl")
    _tomar_el_trial(client, headers)

    sub = db_session.execute(select(Subscription)).scalar_one()
    sub.expires_at = datetime.now(UTC) - timedelta(hours=2)
    db_session.commit()

    with patch(
        "paes_api.modules.billing.flow.suscripcion_estado",
        side_effect=flow.FlowError("Flow caído"),
    ):
        revisadas = service.sincronizar_todas(db_session)

    assert revisadas == 0
    db_session.refresh(sub)
    assert sub.status is SubscriptionStatus.ACTIVE


def test_puede_rendir_corta_solo_con_los_limites_activos(
    register_user, db_session, monkeypatch
) -> None:
    """El muro del plan Gratis: con LIMITES_ACTIVOS el tope bloquea; sin él, se
    informa pero deja seguir.

    Es la palanca que enciende el cobro de verdad, y encenderla antes de que
    exista la salida --pagar o empezar la prueba-- deja al alumno atrapado en
    una pantalla que le pide algo que todavía no puede hacer. Por eso el flag
    arranca apagado y esto comprueba las dos posiciones.

    Viene de la rama `pablo/trial-suscripcion-flow`, que probaba esto y esta no.
    """
    register_user(email="lim1@milpaes.cl")
    user = _usuario(db_session, "lim1@milpaes.cl")  # plan Gratis

    try:
        monkeypatch.setenv("LIMITES_ACTIVOS", "true")
        get_settings.cache_clear()
        with patch(
            "paes_api.modules.billing.service.ensayos_del_mes", return_value=999
        ):
            permitido, motivo = service.puede_rendir(db_session, user.id)
        assert permitido is False
        assert motivo is not None

        monkeypatch.delenv("LIMITES_ACTIVOS", raising=False)
        get_settings.cache_clear()
        with patch(
            "paes_api.modules.billing.service.ensayos_del_mes", return_value=999
        ):
            permitido_sin_flag, _ = service.puede_rendir(db_session, user.id)
        assert permitido_sin_flag is True
    finally:
        monkeypatch.delenv("LIMITES_ACTIVOS", raising=False)
        get_settings.cache_clear()
