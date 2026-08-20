"""El embudo por campaña.

Es la pantalla que decide dónde se gasta la plata de publicidad, así que lo que
se fija acá es la atribución: a qué campaña le cuenta cada visitante, y qué se
considera "pagó".
"""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from paes_api.modules.billing.models import Pago, PagoStatus, Plan
from paes_api.modules.exam_focus.models import AttemptStatus, ExamAttempt
from paes_api.modules.metrics.models import PageView
from paes_api.modules.users.models import User


def _hacer_admin(db: Session, email: str) -> User:
    user = db.execute(select(User).where(User.email == email)).scalar_one()
    user.is_admin = True
    db.commit()
    return user


def _visita(
    db: Session,
    visitor_id: str,
    *,
    campana: str | None = None,
    contenido: str | None = None,
    user_id: int | None = None,
    hace_minutos: int = 0,
) -> None:
    db.add(
        PageView(
            path="/",
            visitor_id=visitor_id,
            user_id=user_id,
            utm_source="instagram" if campana else None,
            utm_medium="cpc" if campana else None,
            utm_campaign=campana,
            utm_content=contenido,
            created_at=datetime.now(UTC) - timedelta(minutes=hace_minutos),
        )
    )
    db.commit()


def _campanas(client: TestClient, headers: dict[str, str]) -> list[dict]:
    resp = client.get("/api/admin/metrics", headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()["campanas"]


def test_los_utm_de_la_url_llegan_a_la_visita(
    client: TestClient, db_session: Session
) -> None:
    """Sin esto no se puede distinguir un anuncio de otro: el navegador interno
    de Instagram muchas veces no manda referrer."""
    resp = client.post(
        "/api/metrics/pageview",
        json={
            "path": "/",
            "visitor_id": "visitante-utm-1",
            "utm_source": "instagram",
            "utm_medium": "cpc",
            "utm_campaign": "lanzamiento-agosto",
            "utm_content": "video-15s",
        },
    )
    assert resp.status_code == 204

    visita = db_session.execute(select(PageView)).scalar_one()
    assert visita.utm_campaign == "lanzamiento-agosto"
    assert visita.utm_content == "video-15s"


def test_una_etiqueta_en_blanco_se_guarda_como_nula(
    client: TestClient, db_session: Session
) -> None:
    """"?utm_campaign=" no es una campaña llamada cadena vacía."""
    client.post(
        "/api/metrics/pageview",
        json={"path": "/", "visitor_id": "visitante-vacio", "utm_campaign": "   "},
    )
    assert db_session.execute(select(PageView)).scalar_one().utm_campaign is None


def test_una_etiqueta_larguisima_se_recorta_y_no_rompe_la_visita(
    client: TestClient, db_session: Session
) -> None:
    """La etiqueta viene de la URL, o sea de fuera. Medir no puede romper la
    navegación, así que se recorta en vez de rechazar."""
    resp = client.post(
        "/api/metrics/pageview",
        json={"path": "/", "visitor_id": "visitante-largo", "utm_campaign": "x" * 250},
    )
    assert resp.status_code == 204
    assert len(db_session.execute(select(PageView)).scalar_one().utm_campaign) == 100


def test_el_visitante_cuenta_para_la_primera_campana_que_lo_trajo(
    client: TestClient, register_user, db_session: Session
) -> None:
    """Atribución de primer toque: quien llega por un anuncio y vuelve por otro
    le cuenta al primero. Repartir el crédito entre toques exige inventar
    pesos, y este panel decide dónde se gasta la plata."""
    headers, _ = register_user(email="jefa@milpaes.cl")
    _hacer_admin(db_session, "jefa@milpaes.cl")

    _visita(db_session, "vuelve", campana="primera", hace_minutos=60)
    _visita(db_session, "vuelve", campana="segunda", hace_minutos=10)

    campanas = {c["campaign"]: c for c in _campanas(client, headers)}
    assert campanas["primera"]["visitantes"] == 1
    assert "segunda" not in campanas


def test_el_trafico_sin_campana_es_una_fila_mas(
    client: TestClient, register_user, db_session: Session
) -> None:
    """Sin esa fila la tabla no suma el total y no se ve qué parte del tráfico
    está atribuida, que es lo primero que hay que saber."""
    headers, _ = register_user(email="jefa@milpaes.cl")
    _hacer_admin(db_session, "jefa@milpaes.cl")

    _visita(db_session, "con-anuncio", campana="lanzamiento")
    _visita(db_session, "directo")

    campanas = _campanas(client, headers)
    sin_campana = [c for c in campanas if c["campaign"] is None]
    assert len(sin_campana) == 1
    assert sin_campana[0]["visitantes"] == 1
    # Y va al final: es el contexto, no la respuesta.
    assert campanas[-1]["campaign"] is None


def test_el_embudo_sigue_al_visitante_hasta_el_pago(
    client: TestClient, register_user, db_session: Session
) -> None:
    headers, _ = register_user(email="jefa@milpaes.cl")
    admin = _hacer_admin(db_session, "jefa@milpaes.cl")

    # El mismo navegador: primero anónimo por el anuncio, después con cuenta.
    _visita(db_session, "convierte", campana="lanzamiento", hace_minutos=30)
    _visita(db_session, "convierte", user_id=admin.id, hace_minutos=20)

    db_session.add(
        ExamAttempt(
            user_id=admin.id,
            duration_limit_seconds=8400,
            status=AttemptStatus.SUBMITTED,
        )
    )
    db_session.add(
        Pago(
            user_id=admin.id,
            orden="orden-1",
            plan=Plan.PRO,
            dias=30,
            monto=5990,
            status=PagoStatus.PAGADO,
        )
    )
    db_session.commit()

    fila = next(c for c in _campanas(client, headers) if c["campaign"] == "lanzamiento")
    assert fila["visitantes"] == 1
    assert fila["registrados"] == 1
    assert fila["con_ensayo_terminado"] == 1
    assert fila["pagaron"] == 1
    assert fila["tasa_pago"] == 1.0


def test_un_plan_regalado_con_codigo_no_cuenta_como_pago(
    client: TestClient, register_user, db_session: Session
) -> None:
    """Una suscripción por código es real, pero no es plata que entró.
    Contarla haría que la campaña parezca rentable con dinero que nadie pagó."""
    headers, _ = register_user(email="jefa@milpaes.cl")
    admin = _hacer_admin(db_session, "jefa@milpaes.cl")

    _visita(db_session, "regalado", campana="lanzamiento", hace_minutos=30)
    _visita(db_session, "regalado", user_id=admin.id, hace_minutos=20)
    db_session.add(
        Pago(
            user_id=admin.id,
            orden="orden-pendiente",
            plan=Plan.PRO,
            dias=30,
            monto=5990,
            status=PagoStatus.PENDIENTE,
        )
    )
    db_session.commit()

    fila = next(c for c in _campanas(client, headers) if c["campaign"] == "lanzamiento")
    assert fila["registrados"] == 1
    assert fila["pagaron"] == 0


def test_dos_creatividades_de_la_misma_campana_son_dos_filas(
    client: TestClient, register_user, db_session: Session
) -> None:
    """Saber que "lanzamiento" funciona no sirve para decidir qué anuncio
    repetir: la creatividad es la unidad que se cambia."""
    headers, _ = register_user(email="jefa@milpaes.cl")
    _hacer_admin(db_session, "jefa@milpaes.cl")

    _visita(db_session, "v1", campana="lanzamiento", contenido="video-15s")
    _visita(db_session, "v2", campana="lanzamiento", contenido="carrusel")

    filas = [c for c in _campanas(client, headers) if c["campaign"] == "lanzamiento"]
    assert sorted(f["content"] for f in filas) == ["carrusel", "video-15s"]
