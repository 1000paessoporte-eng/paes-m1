from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import paes_api.all_models  # noqa: F401 — registra todos los modelos antes de create_all
from paes_api.core.database import get_db
from paes_api.core.limiter import limiter
from paes_api.main import app
from paes_api.shared.base import Base


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    #: SQLite en memoria por test, StaticPool para que todos los threads del
    #: threadpool de FastAPI (los endpoints son `def`, no `async def`, así
    #: que Starlette los corre en threads distintos) compartan la misma
    #: conexión en vez de ver bases de datos vacías cada uno.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_local()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    #: Los endpoints de auth tienen rate limiting (ver core/limiter.py); sin
    #: resetear el storage entre tests, un test que golpea /login varias
    #: veces puede hacer que el siguiente test reciba 429 en vez de 401/200.
    limiter.reset()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def register_user(client: TestClient):
    def _register(
        email: str = "demo@milpaes.cl", password: str = "clave1234", name: str = "Demo"
    ) -> tuple[dict[str, str], dict]:
        resp = client.post(
            "/api/auth/register",
            json={"email": email, "password": password, "name": name},
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        return {"Authorization": f"Bearer {body['access_token']}"}, body["user"]

    return _register
