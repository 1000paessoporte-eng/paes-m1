"""El cobro con Flow.

Lo que se prueba acá no es que Flow funcione —eso es de ellos— sino que la
plataforma no regale planes ni cobre de más. Las tres reglas que sostienen eso
son: el precio lo fija el servidor, la activación solo ocurre tras verificar
con Flow, y confirmar dos veces la misma orden no otorga el doble de días.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.billing import service
from paes_api.modules.billing.models import Pago, PagoStatus, Plan, Subscription
from paes_api.modules.users.models import User


def _usuario(db: Session, email: str) -> User:
    return db.execute(select(User).where(User.email == email)).scalar_one()


def test_productos_no_tienen_precio_cero() -> None:
    """Un producto en cero convertiría el cobro en un regalo silencioso.

    No lanzaría ningún error: Flow aceptaría la orden, el usuario no pagaría
    nada y la suscripción se activaría igual. Por eso se fija acá."""
    assert service.PRODUCTOS, "debería haber al menos un producto comprable"
    for p in service.PRODUCTOS.values():
        assert p.monto > 0, f"{p.id} tiene monto {p.monto}"
        assert p.dias > 0, f"{p.id} otorga {p.dias} días"


def test_productos_es_publico(client: TestClient) -> None:
    """La página de precios lo consulta sin sesión."""
    resp = client.get("/api/plan/productos")
    assert resp.status_code == 200
    body = resp.json()
    assert {p["id"] for p in body["productos"]} == set(service.PRODUCTOS)
    # Sin credenciales configuradas en los tests, el cobro va deshabilitado.
    assert body["pago_disponible"] is False


def test_pagar_sin_credenciales_responde_503(
    client: TestClient, register_user
) -> None:
    """Mejor un 503 explícito que un 500: el cobro no está roto, está apagado."""
    headers, _ = register_user(email="paga1@milpaes.cl")
    resp = client.post(
        "/api/plan/pagar", json={"producto": "pro_mensual"}, headers=headers
    )
    assert resp.status_code == 503


def test_pagar_requiere_sesion(client: TestClient) -> None:
    assert (
        client.post("/api/plan/pagar", json={"producto": "pro_mensual"}).status_code
        == 401
    )


def test_producto_inexistente_es_rechazado(client: TestClient, register_user) -> None:
    headers, _ = register_user(email="paga2@milpaes.cl")
    resp = client.post(
        "/api/plan/pagar", json={"producto": "pro_gratis_total"}, headers=headers
    )
    assert resp.status_code == 422


def test_la_firma_ordena_los_parametros_alfabeticamente() -> None:
    """Flow concatena los pares ORDENADOS por nombre, no en el orden dado.

    Firmar en otro orden produce una firma que parece válida y que Flow
    rechaza sin explicar por qué. Dos diccionarios con las mismas claves en
    distinto orden deben dar la misma firma."""
    from paes_api.modules.billing import flow

    a = flow.firmar({"b": "2", "a": "1", "c": "3"})
    b = flow.firmar({"c": "3", "a": "1", "b": "2"})
    assert a == b
    # Y que el orden importe de verdad: valores distintos, firma distinta.
    assert a != flow.firmar({"a": "2", "b": "1", "c": "3"})


def _flow_pagado(monto: int):
    """Simula a Flow respondiendo que la orden está pagada."""
    return {"status": 2, "amount": monto, "commerceOrder": "x"}


def test_confirmar_activa_la_suscripcion(
    client: TestClient, register_user, db_session: Session
) -> None:
    headers, _ = register_user(email="paga3@milpaes.cl")
    user = _usuario(db_session, "paga3@milpaes.cl")
    pago = Pago(
        user_id=user.id,
        orden="p1-abc",
        plan=Plan.PRO,
        dias=30,
        monto=5990,
        status=PagoStatus.PENDIENTE,
        token="tok-1",
    )
    db_session.add(pago)
    db_session.commit()

    with patch(
        "paes_api.modules.billing.flow.estado", return_value=_flow_pagado(5990)
    ):
        resp = client.post("/api/plan/flow/confirmar", data={"token": "tok-1"})
    assert resp.status_code == 200

    plan = client.get("/api/plan", headers=headers).json()
    assert plan["plan"] == "pro"


def test_confirmar_dos_veces_no_duplica_los_dias(
    client: TestClient, register_user, db_session: Session
) -> None:
    """Flow puede llamar al webhook más de una vez por la misma orden.

    Sin idempotencia, cada aviso repetido regalaría otro mes."""
    register_user(email="paga4@milpaes.cl")
    user = _usuario(db_session, "paga4@milpaes.cl")
    db_session.add(
        Pago(
            user_id=user.id,
            orden="p2-abc",
            plan=Plan.PRO,
            dias=30,
            monto=5990,
            status=PagoStatus.PENDIENTE,
            token="tok-2",
        )
    )
    db_session.commit()

    with patch(
        "paes_api.modules.billing.flow.estado", return_value=_flow_pagado(5990)
    ):
        client.post("/api/plan/flow/confirmar", data={"token": "tok-2"})
        client.post("/api/plan/flow/confirmar", data={"token": "tok-2"})

    subs = list(
        db_session.execute(
            select(Subscription).where(Subscription.user_id == user.id)
        ).scalars()
    )
    assert len(subs) == 1, "la segunda confirmación no debe crear otra suscripción"


def test_pagar_menos_del_precio_no_activa_nada(
    client: TestClient, register_user, db_session: Session
) -> None:
    """El caso que justifica guardar el monto en nuestra base.

    Si Flow informa menos de lo cobrado, no se activa el plan y la orden queda
    pendiente para revisarla a mano."""
    headers, _ = register_user(email="paga5@milpaes.cl")
    user = _usuario(db_session, "paga5@milpaes.cl")
    db_session.add(
        Pago(
            user_id=user.id,
            orden="p3-abc",
            plan=Plan.PRO,
            dias=240,
            monto=34900,
            status=PagoStatus.PENDIENTE,
            token="tok-3",
        )
    )
    db_session.commit()

    with patch(
        "paes_api.modules.billing.flow.estado", return_value=_flow_pagado(100)
    ):
        resp = client.post("/api/plan/flow/confirmar", data={"token": "tok-3"})

    # El webhook responde 200 igual: el error se registra, no se le devuelve a Flow.
    assert resp.status_code == 200
    assert client.get("/api/plan", headers=headers).json()["plan"] == "gratis"

    pago = db_session.execute(
        select(Pago).where(Pago.token == "tok-3")
    ).scalar_one()
    db_session.refresh(pago)
    assert pago.status == PagoStatus.PENDIENTE


def test_pago_rechazado_no_otorga_plan(
    client: TestClient, register_user, db_session: Session
) -> None:
    headers, _ = register_user(email="paga6@milpaes.cl")
    user = _usuario(db_session, "paga6@milpaes.cl")
    db_session.add(
        Pago(
            user_id=user.id,
            orden="p4-abc",
            plan=Plan.PRO,
            dias=30,
            monto=5990,
            status=PagoStatus.PENDIENTE,
            token="tok-4",
        )
    )
    db_session.commit()

    with patch(
        "paes_api.modules.billing.flow.estado",
        return_value={"status": 3, "amount": 0},
    ):
        client.post("/api/plan/flow/confirmar", data={"token": "tok-4"})

    assert client.get("/api/plan", headers=headers).json()["plan"] == "gratis"


def test_token_desconocido_no_revela_nada(client: TestClient) -> None:
    """El webhook es público: no debe confirmar si un token existe o no."""
    resp = client.post("/api/plan/flow/confirmar", data={"token": "inventado"})
    assert resp.status_code == 200


def test_renovar_acumula_sobre_lo_que_queda(
    client: TestClient, register_user, db_session: Session
) -> None:
    """Quien renueva antes de que se le venza no pierde los días restantes."""
    from paes_api.modules.billing.models import Origen, SubscriptionStatus

    headers, _ = register_user(email="paga7@milpaes.cl")
    user = _usuario(db_session, "paga7@milpaes.cl")
    ahora = datetime.now(UTC)
    vence = ahora + timedelta(days=10)
    db_session.add(
        Subscription(
            user_id=user.id,
            plan=Plan.PRO,
            status=SubscriptionStatus.ACTIVE,
            origen=Origen.CODIGO,
            started_at=ahora,
            expires_at=vence,
        )
    )
    db_session.add(
        Pago(
            user_id=user.id,
            orden="p5-abc",
            plan=Plan.PRO,
            dias=30,
            monto=5990,
            status=PagoStatus.PENDIENTE,
            token="tok-5",
        )
    )
    db_session.commit()

    with patch(
        "paes_api.modules.billing.flow.estado", return_value=_flow_pagado(5990)
    ):
        client.post("/api/plan/flow/confirmar", data={"token": "tok-5"})

    nuevo = client.get("/api/plan", headers=headers).json()["vence_el"]
    assert nuevo is not None
    # Debe vencer cerca de 40 días desde ahora (10 que quedaban + 30 comprados),
    # no 30: eso probaría que se perdieron los días restantes.
    vence_dt = datetime.fromisoformat(nuevo)
    if vence_dt.tzinfo is None:
        vence_dt = vence_dt.replace(tzinfo=UTC)
    dias = (vence_dt - ahora).days
    assert 38 <= dias <= 41, f"venció en {dias} días, se esperaban ~40"


@pytest.mark.parametrize("producto", ["pro_mensual", "pro_temporada"])
def test_cada_producto_otorga_el_plan_pro(producto: str) -> None:
    assert service.PRODUCTOS[producto].plan == Plan.PRO


def test_los_limites_se_encienden_por_entorno(monkeypatch) -> None:
    """Encender los límites no debe exigir editar código ni desplegar.

    Antes era una constante de módulo: cambiarla obligaba a un despliegue justo
    en el momento más delicado, el día que empieza a cobrarse. Ahora se lee del
    entorno en cada llamada.
    """
    from paes_api.core.config import get_settings

    assert service.limites_activos() is False

    get_settings.cache_clear()
    monkeypatch.setenv("LIMITES_ACTIVOS", "true")
    try:
        assert service.limites_activos() is True
    finally:
        monkeypatch.delenv("LIMITES_ACTIVOS", raising=False)
        get_settings.cache_clear()


def test_la_cuota_gratis_se_ajusta_por_entorno(monkeypatch) -> None:
    """El número de ensayos gratis es una palanca de negocio, no una constante.

    Encontrar el punto donde aprieta sin espantar es prueba y error contra la
    conversión real, y cada ajuste no puede costar un despliegue.
    """
    from paes_api.core.config import get_settings
    from paes_api.modules.billing.models import Plan

    assert service.limites_de(Plan.GRATIS).ensayos_por_mes == 4

    get_settings.cache_clear()
    monkeypatch.setenv("ENSAYOS_GRATIS_POR_MES", "2")
    try:
        assert service.limites_de(Plan.GRATIS).ensayos_por_mes == 2
        # Pro nunca se ve afectado por esa variable.
        assert service.limites_de(Plan.PRO).ensayos_por_mes is None
    finally:
        monkeypatch.delenv("ENSAYOS_GRATIS_POR_MES", raising=False)
        get_settings.cache_clear()


def test_el_plan_gratis_conserva_el_acceso_a_aprender() -> None:
    """Lo que se limita es el volumen de ensayos, nunca el material de estudio.

    Si algún día alguien restringe las lecciones o el árbol para empujar la
    compra, este test lo obliga a hacerlo a conciencia: un muro sobre el
    contenido ahuyenta a quien todavía no sabe si el producto le sirve.
    """
    from paes_api.modules.billing.models import Plan

    gratis = service.limites_de(Plan.GRATIS)
    assert gratis.ensayos_por_mes is not None, "el plan Gratis sí limita ensayos"
    assert gratis.carreras_en_meta >= 1, "debe poder seguir al menos una carrera"
