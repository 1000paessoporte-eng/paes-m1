"""El desglose por nodo lleva el código del tema, no solo su nombre.

Sin el código, la pantalla de resultados solo puede NOMBRAR el tema que salió
peor: "tu rendimiento fue más bajo en Geometría". Con él puede enlazarlo —a la
lección y a la práctica de ese tema— y el ensayo deja de terminar en un
consejo que el alumno tiene que ejecutar a mano.

Los ejes y las dificultades no son nodos y no tienen página propia: ahí el
código va en None a propósito, y estos tests lo fijan para que nadie lo
"arregle" rellenándolo con el nombre.
"""

from sqlalchemy.orm import Session

from paes_api.modules.content.models import Alternative, Difficulty, Question
from paes_api.modules.exam_focus.service import _tally
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode


def _nodo(db: Session, code: str, name: str) -> SkillNode:
    n = SkillNode(
        code=code, name=name, axis=SkillAxis.GEOMETRIA, tier=1, unlock_threshold=0.75
    )
    db.add(n)
    db.flush()
    db.commit()
    return n


def _pregunta(db: Session, node: SkillNode, stem: str) -> Question:
    q = Question(skill_node_id=node.id, difficulty=Difficulty.MEDIO, stem=stem)
    db.add(q)
    db.flush()
    db.add(Alternative(question_id=q.id, label="A", text="ok", is_correct=True))
    db.commit()
    db.refresh(q)
    return q


def test_el_desglose_por_nodo_trae_el_codigo(db_session: Session) -> None:
    nodo = _nodo(db_session, "geo_areas", "Perímetros y áreas")
    preguntas = [_pregunta(db_session, nodo, f"P{i}") for i in range(2)]

    items = _tally(
        preguntas,
        answers={},
        correct_ids=set(),
        key=lambda q: q.skill_node.name,
        code=lambda q: q.skill_node.code,
    )

    assert len(items) == 1
    assert items[0].name == "Perímetros y áreas"
    assert items[0].code == "geo_areas"


def test_sin_code_el_desglose_lo_deja_en_none(db_session: Session) -> None:
    """Es el caso de los ejes y las dificultades: agrupan, pero no enlazan."""
    nodo = _nodo(db_session, "geo_otro", "Otro tema")
    preguntas = [_pregunta(db_session, nodo, "P")]

    items = _tally(preguntas, answers={}, correct_ids=set(), key=lambda q: "Geometría")

    assert items[0].name == "Geometría"
    assert items[0].code is None


def test_cada_nodo_conserva_su_propio_codigo(db_session: Session) -> None:
    """Dos temas en el mismo ensayo no pueden terminar con el mismo enlace."""
    uno = _nodo(db_session, "geo_areas", "Perímetros y áreas")
    otro = _nodo(db_session, "geo_pitagoras", "Teorema de Pitágoras")
    preguntas = [_pregunta(db_session, uno, "P1"), _pregunta(db_session, otro, "P2")]

    items = _tally(
        preguntas,
        answers={},
        correct_ids=set(),
        key=lambda q: q.skill_node.name,
        code=lambda q: q.skill_node.code,
    )

    por_nombre = {i.name: i.code for i in items}
    assert por_nombre == {
        "Perímetros y áreas": "geo_areas",
        "Teorema de Pitágoras": "geo_pitagoras",
    }
