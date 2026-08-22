"""Borrar la cuenta.

Estaba solo en la política de privacidad como "escríbenos a hola@". Lo que se
fija acá es que borre de verdad --no que esconda-- y que no lo pueda hacer
cualquiera que encuentre una sesión abierta.
"""

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from paes_api.modules.exam_focus.models import AttemptStatus, ExamAttempt
from paes_api.modules.metrics.models import PageView
from paes_api.modules.users.models import User


def test_pide_la_contrasena(client: TestClient, register_user) -> None:
    """Borrar es irreversible: no puede depender solo de que alguien dejó la
    sesión abierta en un computador prestado."""
    headers, _ = register_user(email="borrar@milpaes.cl", password="clave1234")

    assert client.request("DELETE", "/api/auth/me", headers=headers, json={}).status_code == 401
    assert client.request(
        "DELETE", "/api/auth/me", headers=headers, json={"password": "otra"}
    ).status_code == 401


def test_borra_la_cuenta_y_lo_que_cuelga_de_ella(
    client: TestClient, db_session: Session, register_user
) -> None:
    headers, _ = register_user(email="chao@milpaes.cl", password="clave1234")
    user = db_session.execute(select(User).where(User.email == "chao@milpaes.cl")).scalar_one()
    db_session.add(
        ExamAttempt(user_id=user.id, duration_limit_seconds=8400, status=AttemptStatus.SUBMITTED)
    )
    db_session.commit()

    resp = client.request(
        "DELETE", "/api/auth/me", headers=headers, json={"password": "clave1234"}
    )
    assert resp.status_code == 204

    # Se BORRA, no se esconde: una fila con el correo dentro sigue siendo el dato.
    assert db_session.execute(
        select(func.count(User.id)).where(User.email == "chao@milpaes.cl")
    ).scalar_one() == 0
    assert db_session.execute(
        select(func.count(ExamAttempt.id)).where(ExamAttempt.user_id == user.id)
    ).scalar_one() == 0


def test_la_visita_se_conserva_sin_dueno(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Las visitas son estadística agregada del sitio: sin user_id ya no
    identifican a nadie, y borrarlas falsearía el tráfico histórico."""
    headers, _ = register_user(email="visita@milpaes.cl", password="clave1234")
    user = db_session.execute(select(User).where(User.email == "visita@milpaes.cl")).scalar_one()
    db_session.add(PageView(path="/panel", visitor_id="visitante-1234", user_id=user.id))
    db_session.commit()

    client.request("DELETE", "/api/auth/me", headers=headers, json={"password": "clave1234"})

    visita = db_session.execute(select(PageView)).scalar_one()
    assert visita.user_id is None, "la visita pierde el dueño"
    assert visita.path == "/panel", "pero sigue contando como tráfico"


def test_sin_sesion_no_se_borra_nada(client: TestClient) -> None:
    assert client.request("DELETE", "/api/auth/me", json={"password": "x"}).status_code == 401


def test_ninguna_tabla_apunta_a_users_sin_estar_en_el_borrado() -> None:
    """El guardia general: si alguien agrega una tabla que cuelga de `users` y
    no la suma a `eliminar_cuenta`, este test cae y dice exactamente dónde.

    Ya pasó una vez: una tabla nueva quedó fuera de la lista y la baja de
    cuenta habría reventado con violación de clave foránea. Sin este test el
    error solo aparece cuando un usuario real intenta darse de baja, que es el
    peor momento posible para descubrirlo.
    """
    import paes_api.all_models  # noqa: F401 -- puebla Base.metadata
    from paes_api.shared.base import Base

    apuntan_a_users = {
        tabla.name
        for tabla in Base.metadata.tables.values()
        for fk in tabla.foreign_keys
        if fk.column.table.name == "users"
    }

    # Las que `eliminar_cuenta` borra o desvincula hoy. Si agregas una tabla,
    # agrégala también allá y acá.
    cubiertas = {
        "colegios",  # no se borra: el curso pierde a su creador y sigue vivo
        "errores_cliente",  # no se borra: se le quita el dueño
        "exam_attempts",
        "login_events",
        "page_views",  # no se borra: se le quita el dueño
        "pagos",
        "password_reset_tokens",
        "practice_answers",
        "study_streaks",
        "user_goals",  # el modelo se llama MetaUsuario
        "subscriptions",
        "user_skill_progress",
        "users",  # users.colegio_id apunta a colegios, no a users
    }

    faltan = apuntan_a_users - cubiertas
    assert faltan == set(), (
        f"Estas tablas cuelgan de users y no las borra eliminar_cuenta: {sorted(faltan)}. "
        "Agrégalas en users/service.py o el borrado de cuenta va a fallar."
    )


def test_el_profesor_se_borra_y_el_curso_sigue_en_pie(
    client: TestClient, db_session: Session, register_user
) -> None:
    """Adentro del curso hay alumnos que no pidieron nada.

    La política de privacidad promete borrar la cuenta cuando se pide, así que
    negarse no es opción; borrar el curso con sus treinta alumnos adentro,
    tampoco. El colegio pierde a su creador y sigue funcionando.
    """
    from paes_api.modules.colegios.models import Colegio

    profe, _ = register_user(email="profe@milpaes.cl", password="clave1234")
    codigo = client.post(
        "/api/colegio", json={"nombre": "Liceo A-1"}, headers=profe
    ).json()["codigo"]

    alumno, _ = register_user(email="alumna@milpaes.cl", password="clave1234")
    client.post("/api/colegio/unirse", json={"codigo": codigo}, headers=alumno)

    resp = client.request(
        "DELETE", "/api/auth/me", headers=profe, json={"password": "clave1234"}
    )
    assert resp.status_code == 204, resp.text

    colegio = db_session.execute(select(Colegio)).scalars().one()
    assert colegio.creado_por is None
    # Y la alumna sigue adentro, con su curso intacto.
    alumna = db_session.execute(
        select(User).where(User.email == "alumna@milpaes.cl")
    ).scalar_one()
    assert alumna.colegio_id == colegio.id
