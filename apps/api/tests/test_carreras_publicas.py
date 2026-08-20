"""El catálogo público de carreras.

Estas son las únicas rutas del proyecto que visita gente sin cuenta (y Google).
Lo que se prueba acá es justamente eso: que respondan SIN sesión, que un código
inventado dé 404 y no un 500, y que la ficha no filtre nada que no deba salir.
"""

import pytest
from fastapi.testclient import TestClient

from paes_api.modules.goals.models import Carrera


@pytest.fixture()
def carreras(db_session) -> list[Carrera]:
    """Dos carreras: una con requisitos publicados y otra sin ellos.

    La segunda existe porque 1.153 de las 1.855 carreras reales no traen
    `ponderado_min`, y la página tiene que saber mostrarlas igual.
    """
    con_minimo = Carrera(
        codigo="99001",
        universidad="UNIVERSIDAD DE PRUEBA",
        nombre="INGENIERÍA CIVIL",
        sede="SANTIAGO",
        nem=10, ranking=20, lectora=10, m1=35, ciencias=25,
        historia=None, m2=None, prueba_especial=None,
        electivo_alternativo=False,
        ponderado_min=600, promedio_min=550, vacantes=80,
        proceso=2026,
        fuente="https://demre.cl/",
    )
    sin_minimo = Carrera(
        codigo="99002",
        universidad="UNIVERSIDAD DE PRUEBA",
        nombre="ARTE",
        sede="VALPARAÍSO",
        nem=20, ranking=20, lectora=30, m1=10, historia=20,
        ciencias=None, m2=None, prueba_especial=None,
        electivo_alternativo=False,
        ponderado_min=None, promedio_min=None, vacantes=None,
        proceso=2026,
        fuente="https://demre.cl/",
    )
    db_session.add_all([con_minimo, sin_minimo])
    db_session.commit()
    return [con_minimo, sin_minimo]


def test_la_ficha_se_ve_sin_iniciar_sesion(client: TestClient, carreras) -> None:
    """El punto entero de estas páginas: nadie tiene cuenta todavía."""
    res = client.get("/api/carreras/99001")

    assert res.status_code == 200
    datos = res.json()
    assert datos["nombre"] == "INGENIERÍA CIVIL"
    assert datos["universidad"] == "UNIVERSIDAD DE PRUEBA"
    assert datos["m1"] == 35
    assert datos["ponderado_min"] == 600
    assert datos["vacantes"] == 80


def test_la_ficha_dice_de_donde_salio_el_dato(client: TestClient, carreras) -> None:
    """Sin proceso y fuente la página estaría afirmando números sin respaldo."""
    datos = client.get("/api/carreras/99001").json()

    assert datos["proceso"] == 2026
    assert datos["fuente"].startswith("https://")


def test_carrera_sin_requisitos_publicados_responde_igual(
    client: TestClient, carreras
) -> None:
    """1.153 carreras reales no traen ponderado_min: son null, no un error."""
    res = client.get("/api/carreras/99002")

    assert res.status_code == 200
    datos = res.json()
    assert datos["ponderado_min"] is None
    assert datos["promedio_min"] is None
    assert datos["vacantes"] is None
    assert datos["lectora"] == 30


def test_codigo_inexistente_da_404_y_no_500(client: TestClient, carreras) -> None:
    """El código llega desde la URL: cualquiera puede inventarse uno."""
    res = client.get("/api/carreras/00000")

    assert res.status_code == 404


def test_codigo_absurdamente_largo_da_404_sin_reventar(
    client: TestClient, carreras
) -> None:
    """Se acota antes de consultar: una cadena enorme no debe viajar a Postgres."""
    res = client.get("/api/carreras/" + "9" * 500)

    assert res.status_code == 404


def test_el_catalogo_trae_todas_y_solo_lo_necesario(client: TestClient, carreras) -> None:
    """El índice y el sitemap necesitan nombrar y enlazar, nada más."""
    res = client.get("/api/carreras/catalogo")

    assert res.status_code == 200
    datos = res.json()
    assert len(datos) == 2
    assert set(datos[0]) == {"codigo", "universidad", "nombre", "sede"}


def test_el_catalogo_viene_ordenado_estable(client: TestClient, carreras) -> None:
    """Un orden estable evita que el sitemap cambie entero en cada build."""
    datos = client.get("/api/carreras/catalogo").json()

    assert [c["nombre"] for c in datos] == ["ARTE", "INGENIERÍA CIVIL"]


def test_universidades_agrupa_sin_bajar_el_catalogo(
    client: TestClient, carreras: list[Carrera]
) -> None:
    """El índice y la portada solo necesitan las universidades: pedir las 1.855
    filas para contar 47 números es mover un megabyte de más."""
    resp = client.get("/api/carreras/universidades")
    assert resp.status_code == 200
    assert resp.json() == [{"universidad": "UNIVERSIDAD DE PRUEBA", "carreras": 2}]


def test_universidades_no_se_confunde_con_un_codigo_de_carrera(client: TestClient) -> None:
    """La ruta va antes que /{codigo}; si se registrara después, FastAPI leería
    "universidades" como el código de una carrera y contestaría 404."""
    assert client.get("/api/carreras/universidades").status_code == 200


def test_buscar_sin_sesion_encuentra_por_palabras_sueltas(
    client: TestClient, carreras: list[Carrera]
) -> None:
    """La pregunta con la que la gente llega es "cuánto necesito para X", y el
    buscador vivía detrás del login."""
    resp = client.get("/api/carreras/buscar", params={"q": "ingenieria prueba"})
    assert resp.status_code == 200
    assert [c["codigo"] for c in resp.json()] == ["99001"]


def test_buscar_ignora_tildes(client: TestClient, carreras: list[Carrera]) -> None:
    """Nadie escribe "INGENIERÍA" con tilde en un buscador."""
    assert client.get("/api/carreras/buscar", params={"q": "INGENIERÍA"}).json()[0][
        "codigo"
    ] == "99001"


def test_buscar_con_menos_de_tres_letras_no_devuelve_ruido(
    client: TestClient, carreras: list[Carrera]
) -> None:
    """"me" está dentro de medicina, comercio e ingeniería comercial: un
    resultado que no discrimina nada es peor que ninguno."""
    assert client.get("/api/carreras/buscar", params={"q": "in"}).json() == []
    assert client.get("/api/carreras/buscar", params={"q": ""}).json() == []


def test_buscar_no_se_confunde_con_un_codigo(client: TestClient) -> None:
    """La ruta va antes que /{codigo}."""
    assert client.get("/api/carreras/buscar", params={"q": "algo"}).status_code == 200
