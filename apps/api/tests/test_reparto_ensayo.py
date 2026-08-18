"""El ensayo debe repartirse como el temario, no como el banco.

Antes la cuota de cada eje salía del tamaño del banco. Con los nodos parejos en
68, eso convertía "cuántos nodos tiene el eje" en el reparto de la prueba:
Geometría quedaba en 31% por tener 5 nodos para 4 unidades oficiales, y
Probabilidad en 13% por tener 2 nodos para 3 unidades. Estos tests fijan que el
peso venga del temario y no se mueva cuando el banco crezca.
"""

from collections import Counter
from dataclasses import dataclass

from paes_api.modules.exam_focus.service import UNIDADES_POR_EJE, _select_questions
from paes_api.modules.skill_tree.models import SkillAxis


@dataclass
class _Nodo:
    axis: SkillAxis


@dataclass
class _Dif:
    value: str


@dataclass
class _Pregunta:
    id: int
    skill_node: _Nodo
    difficulty: _Dif


def _banco(por_eje: dict[str, int]) -> list[_Pregunta]:
    """Cada eje con un tercio de cada dificultad, como está construido el banco."""
    preguntas, i = [], 0
    for eje, cuantas in por_eje.items():
        for k in range(cuantas):
            i += 1
            nivel = ("facil", "medio", "dificil")[k % 3]
            preguntas.append(_Pregunta(i, _Nodo(SkillAxis(eje)), _Dif(nivel)))
    return preguntas


def _reparto(elegidas: list[_Pregunta]) -> Counter:
    return Counter(q.skill_node.axis.value for q in elegidas)


def test_las_unidades_por_eje_calzan_con_el_temario() -> None:
    """El temario 2027 de M1 lista 16 unidades temáticas repartidas así."""
    assert UNIDADES_POR_EJE == {
        "numeros": 3,
        "algebra": 6,
        "geometria": 4,
        "probabilidad": 3,
    }
    assert sum(UNIDADES_POR_EJE.values()) == 16


def test_un_ensayo_de_65_sigue_el_reparto_del_temario() -> None:
    pool = _banco({"numeros": 300, "algebra": 300, "geometria": 300, "probabilidad": 300})
    reparto = _reparto(_select_questions(pool, [], 65))
    # 3, 6, 4 y 3 unidades sobre 16 dan 12,19 / 24,38 / 16,25 / 12,19. Al
    # truncar suman 64, y la plaza suelta va a Álgebra, que es la de mayor peso
    # y además la de mayor resto.
    assert reparto["algebra"] == 25
    assert reparto["geometria"] == 16
    assert reparto["numeros"] == 12
    assert reparto["probabilidad"] == 12
    assert sum(reparto.values()) == 65


def test_el_reparto_no_depende_del_tamano_del_banco() -> None:
    """Este es el bug que se corrigió: con el reparto viejo, duplicar el banco
    de un eje le duplicaba la presencia en la prueba."""
    equilibrado = _banco({"numeros": 200, "algebra": 200, "geometria": 200, "probabilidad": 200})
    desbalanceado = _banco({"numeros": 200, "algebra": 200, "geometria": 800, "probabilidad": 100})
    assert _reparto(_select_questions(equilibrado, [], 65)) == _reparto(
        _select_questions(desbalanceado, [], 65)
    )


def test_un_ensayo_corto_toca_todos_los_ejes() -> None:
    pool = _banco({"numeros": 100, "algebra": 100, "geometria": 100, "probabilidad": 100})
    reparto = _reparto(_select_questions(pool, [], 20))
    assert set(reparto) == {"numeros", "algebra", "geometria", "probabilidad"}
    assert sum(reparto.values()) == 20


def test_respeta_los_ejes_elegidos_por_el_estudiante() -> None:
    pool = _banco({"numeros": 100, "algebra": 100, "geometria": 100, "probabilidad": 100})
    elegidas = _select_questions(pool, ["algebra", "geometria"], 30)
    reparto = _reparto(elegidas)
    assert set(reparto) == {"algebra", "geometria"}
    # Entre esos dos, 6 y 4 unidades reparten 30 en 18 y 12.
    assert reparto["algebra"] == 18
    assert reparto["geometria"] == 12


def test_no_pide_mas_preguntas_de_las_que_tiene_un_eje() -> None:
    """Si un eje tiene poco banco, su cuota se recorta y el resto se reparte."""
    pool = _banco({"numeros": 5, "algebra": 100, "geometria": 100, "probabilidad": 100})
    elegidas = _select_questions(pool, [], 65)
    reparto = _reparto(elegidas)
    assert reparto["numeros"] <= 5
    assert sum(reparto.values()) == 65


def test_un_ensayo_corto_no_sale_cargado_a_una_dificultad() -> None:
    """Elegir al azar dentro del eje podía dar 12 fáciles en 20 preguntas."""
    pool = _banco(
        {"numeros": 300, "algebra": 300, "geometria": 300, "probabilidad": 300}
    )
    for _ in range(20):
        elegidas = _select_questions(pool, [], 24)
        reparto = Counter(q.difficulty.value for q in elegidas)
        assert set(reparto) == {"facil", "medio", "dificil"}
        # Las tres franjas quedan parejas salvo el sobrante del redondeo, que
        # se acumula a propósito en "medio": es la franja más poblada de una
        # prueba real. Con 24 preguntas eso da 10 / 7 / 7.
        assert max(reparto.values()) - min(reparto.values()) <= 3
        assert reparto["medio"] >= reparto["facil"]
        assert reparto["medio"] >= reparto["dificil"]


def test_el_equilibrio_de_dificultad_aguanta_un_banco_desparejo() -> None:
    """Si una dificultad escasea, se completa con el resto sin fallar."""
    pool = [
        _Pregunta(i, _Nodo(SkillAxis("algebra")), _Dif("facil" if i > 3 else "dificil"))
        for i in range(1, 101)
    ]
    elegidas = _select_questions(pool, ["algebra"], 30)
    assert len(elegidas) == 30
