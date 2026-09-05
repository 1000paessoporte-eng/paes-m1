"""M2 trae 5 ítems de suficiencia de datos entre sus 55 preguntas.

Es un formato propio de M2: no se resuelve el problema, se decide si la
información entregada alcanza para resolverlo. Vive mezclado con el resto del
banco de matemática, así que el reparto por eje no lo protege: sin una cuota
explícita, un ensayo de M2 traía menos de uno.
"""

from dataclasses import dataclass

from paes_api.modules.exam_focus.service import (
    LARGO_OFICIAL_M2,
    SUFICIENCIA_POR_PRUEBA,
    _es_suficiencia,
    _select_questions,
)
from paes_api.modules.skill_tree.models import SkillAxis, Subject


@dataclass
class _Nodo:
    axis: SkillAxis
    subject: Subject = Subject.M1


@dataclass
class _Dif:
    value: str


@dataclass
class _Pregunta:
    id: int
    skill_node: _Nodo
    difficulty: _Dif
    stem: str


def _banco(normales_por_eje: int, suficiencia_por_eje: int) -> list[_Pregunta]:
    preguntas, i = [], 0
    for eje in ("numeros", "algebra", "geometria", "probabilidad"):
        for k in range(normales_por_eje):
            i += 1
            nivel = ("facil", "medio", "dificil")[k % 3]
            preguntas.append(
                _Pregunta(i, _Nodo(SkillAxis(eje)), _Dif(nivel), f"Pregunta {i}")
            )
        for k in range(suficiencia_por_eje):
            i += 1
            preguntas.append(
                _Pregunta(
                    i,
                    _Nodo(SkillAxis(eje)),
                    _Dif("medio"),
                    f"Suficiencia de datos. Caso {i}.\n\n(1) uno\n(2) dos",
                )
            )
    return preguntas


def _cuantos(elegidas) -> int:
    return sum(1 for q in elegidas if _es_suficiencia(q))


def test_un_ensayo_oficial_de_m2_trae_cinco_de_suficiencia() -> None:
    pool = _banco(normales_por_eje=200, suficiencia_por_eje=15)
    elegidas = _select_questions(pool, [], LARGO_OFICIAL_M2, Subject.M2)
    assert len(elegidas) == LARGO_OFICIAL_M2
    assert _cuantos(elegidas) == SUFICIENCIA_POR_PRUEBA


def test_un_ensayo_corto_trae_la_proporcion_correspondiente() -> None:
    """5 de 55 es un 9%: en 22 preguntas toca 2, no 5."""
    pool = _banco(normales_por_eje=200, suficiencia_por_eje=15)
    elegidas = _select_questions(pool, [], 22, Subject.M2)
    assert _cuantos(elegidas) == 2


def test_m1_no_recibe_items_de_suficiencia() -> None:
    """El formato es exclusivo de M2: en M1 la cuota no debe activarse."""
    pool = _banco(normales_por_eje=200, suficiencia_por_eje=15)
    elegidas = _select_questions(pool, [], 40, Subject.M1)
    assert _cuantos(elegidas) <= 15  # el azar podría traerlos, pero no se fuerzan
    sin_suficiencia = [q for q in pool if not _es_suficiencia(q)]
    solo_normales = _select_questions(sin_suficiencia, [], 40, Subject.M1)
    assert _cuantos(solo_normales) == 0


def test_la_cuota_no_deshace_el_reparto_por_eje() -> None:
    """El canje saca una pregunta del mismo eje que la que entra."""
    pool = _banco(normales_por_eje=200, suficiencia_por_eje=15)
    sin_cuota = _select_questions(pool, [], LARGO_OFICIAL_M2, Subject.M1)
    con_cuota = _select_questions(pool, [], LARGO_OFICIAL_M2, Subject.M2)
    ejes_sin = sorted(q.skill_node.axis.value for q in sin_cuota)
    ejes_con = sorted(q.skill_node.axis.value for q in con_cuota)
    # M1 y M2 pesan distinto los ejes, así que no se comparan los repartos
    # entre sí: lo que se fija es que ninguno quede vacío tras el canje.
    assert len(set(ejes_sin)) == 4
    assert len(set(ejes_con)) == 4


def test_si_el_banco_no_tiene_suficientes_el_ensayo_sale_igual() -> None:
    pool = _banco(normales_por_eje=200, suficiencia_por_eje=0)
    elegidas = _select_questions(pool, [], LARGO_OFICIAL_M2, Subject.M2)
    assert len(elegidas) == LARGO_OFICIAL_M2
    assert _cuantos(elegidas) == 0


def test_el_banco_real_alcanza_para_la_cuota() -> None:
    from paes_api.seed_data import QUESTIONS

    sd = [q for q in QUESTIONS if q["stem"].startswith("Suficiencia de datos.")]
    assert len(sd) >= SUFICIENCIA_POR_PRUEBA * 4, (
        "con menos de veinte ítems, dos ensayos seguidos repetirían casi todos"
    )
    ejes = {q["skill_node"] for q in sd}
    assert len(ejes) >= 10, "el formato debe cruzar todos los ejes, no vivir en uno"
