"""El trial con tarjeta y la suscripción recurrente de Flow.

Flow no se toca de verdad: cada función que habla con la pasarela se reemplaza
por un doble que devuelve lo que Flow devolvería. Lo que se prueba es la lógica
propia —a quién se le da acceso, cuándo, y que un cobro no se cuente dos veces—,
no la API de Flow.
"""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.billing import service
from paes_api.modules.billing.models import (
    ClienteFlow,
    EstadoFlow,
    Pago,
    Plan,
    Subscription,
    SubscriptionStatus,
)
from paes_api.modules.users.models import User

_SETTINGS = SimpleNamespace(flow_plan_id="pro_mensual", trial_dias=3)


def _usuario(db: Session, email: str) -> User:
    return db.execute(select(User).where(User.email == email)).scalar_one()


def _plan_vigente(db: Session, user_id: int) -> Plan:
    return service.plan_actual(db, user_id)[0]


def test_iniciar_trial_crea_cliente_y_devuelve_url(register_user, db_session) -> None:
    register_user(email="trial1@milpaes.cl")
    user = _usuario(db_session, "trial1@milpaes.cl")

    with (
        patch("paes_api.modules.billing.flow.esta_configurado", return_value=True),
        patch("paes_api.modules.billing.service.get_settings", return_value=_SETTINGS),
        patch(
            "paes_api.modules.billing.flow.crear_cliente",
            return_value={"customerId": "cus_1"},
        ),
        patch(
            "paes_api.modules.billing.flow.registrar_tarjeta",
            return_value={"url": "https://flow/registro", "token": "regtok_1"},
        ),
    ):
        url = service.iniciar_trial(db_session, user, url_retorno="https://front/tarjeta")

    assert url == "https://flow/registro"
    cliente = db_session.execute(
        select(ClienteFlow).where(ClienteFlow.user_id == user.id)
    ).scalar_one()
    assert cliente.flow_customer_id == "cus_1"
    assert cliente.registro_token == "regtok_1"
    assert cliente.status == EstadoFlow.REGISTRANDO
    # El trial aún no otorga acceso: primero hay que registrar la tarjeta.
    assert _plan_vigente(db_session, user.id) is Plan.GRATIS


def test_no_da_trial_a_quien_ya_tiene_plan(register_user, db_session) -> None:
    register_user(email="trial2@milpaes.cl")
    user = _usuario(db_session, "trial2@milpaes.cl")
    db_session.add(
        Subscription(
            user_id=user.id,
            plan=Plan.PRO,
            status=SubscriptionStatus.ACTIVE,
            expires_at=datetime.now(UTC) + timedelta(days=10),
        )
    )
    db_session.commit()

    with (
        patch("paes_api.modules.billing.flow.esta_configurado", return_value=True),
        patch("paes_api.modules.billing.service.get_settings", return_value=_SETTINGS),
        pytest.raises(service.TrialNoDisponible),
    ):
        service.iniciar_trial(db_session, user, url_retorno="https://front/tarjeta")


def test_confirmar_tarjeta_ok_suscribe_y_da_los_dias(register_user, db_session) -> None:
    register_user(email="trial3@milpaes.cl")
    user = _usuario(db_session, "trial3@milpaes.cl")
    db_session.add(
        ClienteFlow(
            user_id=user.id,
            flow_customer_id="cus_3",
            registro_token="regtok_3",
            status=EstadoFlow.REGISTRANDO,
        )
    )
    db_session.commit()

    with (
        patch("paes_api.modules.billing.service.get_settings", return_value=_SETTINGS),
        patch(
            "paes_api.modules.billing.flow.estado_tarjeta",
            return_value={"status": 1},
        ),
        patch(
            "paes_api.modules.billing.flow.crear_suscripcion",
            return_value={"subscriptionId": "sub_3"},
        ),
    ):
        service.confirmar_tarjeta(db_session, user.id)

    cliente = db_session.execute(
        select(ClienteFlow).where(ClienteFlow.user_id == user.id)
    ).scalar_one()
    assert cliente.flow_subscription_id == "sub_3"
    assert cliente.status == EstadoFlow.TRIAL
    # Ya tiene Pro por los días de prueba.
    assert _plan_vigente(db_session, user.id) is Plan.PRO


def test_confirmar_tarjeta_no_registrada_no_da_acceso(register_user, db_session) -> None:
    register_user(email="trial4@milpaes.cl")
    user = _usuario(db_session, "trial4@milpaes.cl")
    db_session.add(
        ClienteFlow(
            user_id=user.id,
            flow_customer_id="cus_4",
            registro_token="regtok_4",
            status=EstadoFlow.REGISTRANDO,
        )
    )
    db_session.commit()

    with (
        patch("paes_api.modules.billing.service.get_settings", return_value=_SETTINGS),
        patch("paes_api.modules.billing.flow.estado_tarjeta", return_value={"status": 0}),
        pytest.raises(service.TarjetaNoRegistrada),
    ):
        service.confirmar_tarjeta(db_session, user.id)

    cliente = db_session.execute(
        select(ClienteFlow).where(ClienteFlow.user_id == user.id)
    ).scalar_one()
    assert cliente.status == EstadoFlow.FALLIDA
    assert cliente.flow_subscription_id is None
    assert _plan_vigente(db_session, user.id) is Plan.GRATIS


def test_cobro_recurrente_extiende_un_mes_y_es_idempotente(
    register_user, db_session
) -> None:
    register_user(email="trial5@milpaes.cl")
    user = _usuario(db_session, "trial5@milpaes.cl")
    db_session.add(
        ClienteFlow(
            user_id=user.id,
            flow_customer_id="cus_5",
            flow_subscription_id="sub_5",
            status=EstadoFlow.TRIAL,
        )
    )
    db_session.commit()

    una_invoice = {"invoices": [{"id": "inv_1", "status": 2, "amount": 9990}]}
    with patch(
        "paes_api.modules.billing.flow.estado_suscripcion", return_value=una_invoice
    ):
        service.procesar_cobro_recurrente(db_session, "sub_5")
        # Segundo aviso por el MISMO cobro: no debe extender de nuevo.
        service.procesar_cobro_recurrente(db_session, "sub_5")

    pagos = db_session.execute(
        select(Pago).where(Pago.user_id == user.id)
    ).scalars().all()
    assert len(pagos) == 1  # el cobro se registró una sola vez
    assert pagos[0].monto == 9990

    subs = db_session.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    ).scalars().all()
    assert len(subs) == 1  # un solo mes otorgado
    assert _plan_vigente(db_session, user.id) is Plan.PRO
    cliente = db_session.execute(
        select(ClienteFlow).where(ClienteFlow.user_id == user.id)
    ).scalar_one()
    assert cliente.status == EstadoFlow.ACTIVA


def test_mi_plan_dice_que_estas_en_prueba(register_user, client, db_session) -> None:
    """El panel necesita distinguir la prueba del Pro pagado para avisar cuándo
    se cobra y que cancelar ahora no cuesta."""
    headers, _ = register_user(email="trial6@milpaes.cl")
    user = _usuario(db_session, "trial6@milpaes.cl")
    db_session.add(
        ClienteFlow(
            user_id=user.id,
            flow_customer_id="cus_6",
            flow_subscription_id="sub_6",
            status=EstadoFlow.TRIAL,
        )
    )
    db_session.add(
        Subscription(
            user_id=user.id,
            plan=Plan.PRO,
            status=SubscriptionStatus.ACTIVE,
            expires_at=datetime.now(UTC) + timedelta(days=3),
        )
    )
    db_session.commit()

    datos = client.get("/api/plan", headers=headers).json()
    assert datos["plan"] == "pro"
    assert datos["en_prueba"] is True
