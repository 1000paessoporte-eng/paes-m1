import re

from fastapi.testclient import TestClient

from paes_api.modules.users import service as users_service


def test_register_creates_user_and_token(client: TestClient) -> None:
    resp = client.post(
        "/api/auth/register",
        json={"email": "nueva@milpaes.cl", "password": "clave1234", "name": "Nueva"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["email"] == "nueva@milpaes.cl"
    assert body["access_token"]


def test_register_duplicate_email_is_conflict(client: TestClient, register_user) -> None:
    register_user(email="dup@milpaes.cl")
    resp = client.post(
        "/api/auth/register",
        json={"email": "dup@milpaes.cl", "password": "clave1234", "name": "Otra"},
    )
    assert resp.status_code == 409


def test_login_success(client: TestClient, register_user) -> None:
    register_user(email="login@milpaes.cl", password="clave1234")
    resp = client.post(
        "/api/auth/login", json={"email": "login@milpaes.cl", "password": "clave1234"}
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_wrong_password(client: TestClient, register_user) -> None:
    register_user(email="login2@milpaes.cl", password="clave1234")
    resp = client.post(
        "/api/auth/login", json={"email": "login2@milpaes.cl", "password": "incorrecta"}
    )
    assert resp.status_code == 401


def test_login_unknown_email(client: TestClient) -> None:
    resp = client.post(
        "/api/auth/login", json={"email": "no-existe@milpaes.cl", "password": "clave1234"}
    )
    assert resp.status_code == 401


def test_me_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client: TestClient, register_user) -> None:
    headers, user = register_user(email="me@milpaes.cl")
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == user["email"]


def test_update_me_changes_name_without_touching_password(
    client: TestClient, register_user
) -> None:
    headers, _ = register_user(email="rename@milpaes.cl")
    resp = client.patch("/api/auth/me", json={"name": "Nuevo Nombre"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Nuevo Nombre"


def test_update_me_wrong_current_password_is_rejected(
    client: TestClient, register_user
) -> None:
    headers, _ = register_user(email="pwd@milpaes.cl", password="clave1234")
    resp = client.patch(
        "/api/auth/me",
        json={"current_password": "no-es-esta", "new_password": "otraclave99"},
        headers=headers,
    )
    assert resp.status_code == 401


def test_update_me_correct_current_password_allows_change(
    client: TestClient, register_user
) -> None:
    headers, _ = register_user(email="pwd2@milpaes.cl", password="clave1234")
    resp = client.patch(
        "/api/auth/me",
        json={"current_password": "clave1234", "new_password": "otraclave99"},
        headers=headers,
    )
    assert resp.status_code == 200

    login = client.post(
        "/api/auth/login", json={"email": "pwd2@milpaes.cl", "password": "otraclave99"}
    )
    assert login.status_code == 200


def test_forgot_password_and_reset_flow(
    client: TestClient, register_user, monkeypatch
) -> None:
    register_user(email="reset@milpaes.cl", password="clave1234")

    sent: dict[str, str] = {}

    def fake_send_email(to: str, subject: str, body: str) -> None:
        sent["to"] = to
        sent["body"] = body

    monkeypatch.setattr(users_service, "send_email", fake_send_email)

    resp = client.post("/api/auth/forgot-password", json={"email": "reset@milpaes.cl"})
    assert resp.status_code == 204
    assert sent["to"] == "reset@milpaes.cl"

    match = re.search(r"token=([\w-]+)", sent["body"])
    assert match is not None
    raw_token = match.group(1)

    reset_resp = client.post(
        "/api/auth/reset-password",
        json={"token": raw_token, "new_password": "recuperada99"},
    )
    assert reset_resp.status_code == 204

    # El token ya usado no debe funcionar dos veces.
    reuse_resp = client.post(
        "/api/auth/reset-password",
        json={"token": raw_token, "new_password": "otra-mas"},
    )
    assert reuse_resp.status_code == 400

    login = client.post(
        "/api/auth/login", json={"email": "reset@milpaes.cl", "password": "recuperada99"}
    )
    assert login.status_code == 200


def test_forgot_password_unknown_email_still_returns_204(client: TestClient) -> None:
    """No debe revelar si el correo existe o no."""
    resp = client.post("/api/auth/forgot-password", json={"email": "fantasma@milpaes.cl"})
    assert resp.status_code == 204


def test_reset_password_invalid_token_is_rejected(client: TestClient) -> None:
    resp = client.post(
        "/api/auth/reset-password",
        json={"token": "no-existe-este-token", "new_password": "clave1234"},
    )
    assert resp.status_code == 400


def test_login_is_rate_limited_after_repeated_attempts(
    client: TestClient, register_user
) -> None:
    register_user(email="bruteforce@milpaes.cl", password="clave1234")

    statuses = [
        client.post(
            "/api/auth/login",
            json={"email": "bruteforce@milpaes.cl", "password": "incorrecta"},
        ).status_code
        for _ in range(6)
    ]

    assert statuses[:5] == [401] * 5
    assert statuses[5] == 429
