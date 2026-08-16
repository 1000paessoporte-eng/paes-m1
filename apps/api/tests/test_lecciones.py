"""La teoría de cada nodo del Árbol de Habilidades.

El árbol medía sin enseñar. Estos tests fijan las dos decisiones que hacen que
la lección sirva: que se pueda leer aunque el tema esté bloqueado, y que cada
paso del ejemplo traiga su porqué.
"""

import pytest
from fastapi.testclient import TestClient

from paes_api.seed_data import LESSONS, SKILL_NODES


def test_todo_nodo_de_m1_tiene_leccion() -> None:
    """M1 es la prueba con el banco más grande y la que más se rinde: su
    temario tiene que estar cubierto entero, sin nodos huérfanos."""
    faltan = [n[0] for n in SKILL_NODES if n[0] not in LESSONS]
    assert faltan == [], f"nodos de M1 sin lección: {faltan}"


@pytest.mark.parametrize("codigo", sorted(LESSONS))
def test_cada_paso_explica_por_que(codigo: str) -> None:
    """Un paso sin justificación es una receta para copiar. La estructura
    obliga a que cada uno diga por qué se hace lo que se hace."""
    pasos = LESSONS[codigo]["example_steps"]
    assert len(pasos) >= 2, f"{codigo} tiene {len(pasos)} paso(s)"
    for i, paso in enumerate(pasos, 1):
        assert paso["accion"].strip(), f"{codigo}: paso {i} sin acción"
        assert paso["porque"].strip(), f"{codigo}: paso {i} sin porqué"


@pytest.mark.parametrize("codigo", sorted(LESSONS))
def test_toda_leccion_advierte_el_error_comun(codigo: str) -> None:
    """La trampa en la que cae casi todo el mundo vale tanto como la teoría."""
    assert LESSONS[codigo].get("common_error", "").strip()


def test_leccion_de_nodo_sin_teoria_da_404(client: TestClient, register_user) -> None:
    headers, _ = register_user()
    resp = client.get("/api/skill-tree/no_existe/leccion", headers=headers)
    assert resp.status_code == 404


def test_leccion_exige_sesion(client: TestClient) -> None:
    assert client.get("/api/skill-tree/num_racionales/leccion").status_code == 401
