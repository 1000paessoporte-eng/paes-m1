"""Cifras públicas del banco.

La portada las muestra ("344 preguntas verificadas"), así que este endpoint es
lo que evita que ese número sea una constante escrita a mano que envejece sola.
"""

from fastapi.testclient import TestClient


def test_stats_es_publico(client: TestClient) -> None:
    """Sin token: lo consume la portada, que se ve sin haber iniciado sesión."""
    resp = client.get("/api/questions/stats")
    assert resp.status_code == 200


def test_stats_cuenta_lo_que_hay_en_la_base(client: TestClient) -> None:
    datos = client.get("/api/questions/stats").json()
    assert set(datos) == {"questions", "passages", "skill_nodes", "subjects"}

    # La base de tests arranca vacía: el contrato es informar el estado real,
    # no devolver un número fijo.
    assert datos["questions"] == 0
    assert datos["skill_nodes"] == 0


def test_stats_no_revela_ninguna_pregunta(client: TestClient) -> None:
    """Cuenta preguntas; no las entrega. Un endpoint público que filtrara
    enunciados o respuestas rompería el examen."""
    cuerpo = client.get("/api/questions/stats").text
    assert "stem" not in cuerpo
    assert "alternatives" not in cuerpo
    assert "is_correct" not in cuerpo
