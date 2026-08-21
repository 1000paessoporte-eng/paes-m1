"""La teoría de cada nodo del Árbol de Habilidades.

El árbol medía sin enseñar. Estos tests fijan las dos decisiones que hacen que
la lección sirva: que se pueda leer aunque el tema esté bloqueado, y que cada
paso del ejemplo traiga su porqué.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from paes_api.modules.content.models import Lesson
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode
from paes_api.seed_data import (
    LESSONS,
    SKILL_NODES,
    SKILL_NODES_CIENCIAS,
    SKILL_NODES_HISTORIA,
    SKILL_NODES_LECTORA,
    SKILL_NODES_M2,
)

#: Todos los nodos del árbol, de las cinco pruebas.
TODOS_LOS_NODOS = (
    SKILL_NODES
    + SKILL_NODES_M2
    + SKILL_NODES_LECTORA
    + SKILL_NODES_CIENCIAS
    + SKILL_NODES_HISTORIA
)


def _sembrar_leccion(db_session: Session, code: str) -> SkillNode:
    """Un nodo con su lección escrita."""
    node = SkillNode(
        code=code, name=f"Tema {code}", axis=SkillAxis.NUMEROS, tier=1, unlock_threshold=0.75
    )
    db_session.add(node)
    db_session.flush()
    db_session.add(
        Lesson(
            skill_node_id=node.id,
            intro="Para qué sirve.",
            theory="Lo que hay que saber.",
            example_statement="Calcula 2 + 2.",
            example_steps=[{"accion": "Suma", "porque": "Es una suma"}],
            common_error="Confundirlo con 2 x 2.",
        )
    )
    db_session.commit()
    return node


def test_todo_nodo_tiene_leccion() -> None:
    """Ningún nodo del árbol mide sin enseñar.

    Antes esta exigencia valía solo para M1, porque era la única prueba con
    teoría escrita: Ciencias e Historia tenían doce y seis nodos con cero
    lecciones, y un alumno que elegía esas pruebas encontraba un árbol que lo
    evaluaba y no le explicaba nada. Ahora las cinco están cubiertas, así que
    el test cubre las cinco: agregar un nodo sin su lección vuelve a romper
    acá y no en producción.
    """
    faltan = sorted(n[0] for n in TODOS_LOS_NODOS if n[0] not in LESSONS)
    assert faltan == [], f"nodos sin lección: {faltan}"


def test_ninguna_leccion_apunta_a_un_nodo_inexistente() -> None:
    """Una lección con un código mal escrito no se sube y nadie se entera:
    `seed.py` la salta en silencio porque no encuentra su nodo."""
    codigos = {n[0] for n in TODOS_LOS_NODOS}
    huerfanas = sorted(c for c in LESSONS if c not in codigos)
    assert huerfanas == [], f"lecciones sin nodo: {huerfanas}"


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


def test_leccion_se_lee_sin_sesion(client: TestClient, db_session: Session) -> None:
    """La lección es contenido de enseñanza: no trae ninguna pregunta del banco
    ni ninguna respuesta correcta. Exigir cuenta no protegía nada y dejaba
    fuera de Google lo único que se puede encontrar buscando. Lo que sigue
    pidiendo cuenta es practicar."""
    _sembrar_leccion(db_session, "num_publico")

    resp = client.get("/api/skill-tree/num_publico/leccion")
    assert resp.status_code == 200
    assert resp.json()["node_code"] == "num_publico"


def test_indice_de_lecciones_solo_trae_las_escritas(
    client: TestClient, db_session: Session
) -> None:
    """Un índice que promete todos los temas y entrega las lecciones que
    existen manda a Google a una ristra de 404."""
    _sembrar_leccion(db_session, "con_leccion")
    db_session.add(
        SkillNode(
            code="sin_leccion",
            name="Tema sin lección",
            axis=SkillAxis.NUMEROS,
            tier=1,
            unlock_threshold=0.75,
        )
    )
    db_session.commit()

    body = client.get("/api/skill-tree/lecciones").json()
    assert [item["node_code"] for item in body] == ["con_leccion"]
    assert body[0]["axis_label"] == "Números"


def test_indice_no_se_confunde_con_el_codigo_de_un_nodo(client: TestClient) -> None:
    """La ruta va antes que /{code}; registrada después, FastAPI leería
    "lecciones" como el código de un nodo."""
    assert client.get("/api/skill-tree/lecciones").status_code == 200
