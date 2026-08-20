"""El reparto del tiempo entre las preguntas del ensayo.

Dividir en partes iguales trataba igual una pregunta de operatoria directa que
una de geometría con figura. Lo que se fija acá es que el reparto sea distinto
POR pregunta sin inventar tiempo: la suma tiene que seguir siendo la duración
real del intento.
"""

from paes_api.modules.content.models import Difficulty, Question, ReadingPassage
from paes_api.modules.exam_focus.service import tiempos_sugeridos


def _q(qid: int, dificultad: Difficulty, passage=None) -> Question:
    q = Question(skill_node_id=1, difficulty=dificultad, stem=f"P{qid}")
    q.id = qid
    q.passage_id = passage.id if passage else None
    q.passage = passage
    return q


def test_la_suma_es_exactamente_la_duracion_del_ensayo() -> None:
    """El alumno que respeta todos los presupuestos termina justo a tiempo.
    Si la suma se pasara, la pantalla le estaría prometiendo tiempo que la
    prueba no le da."""
    preguntas = [
        _q(1, Difficulty.FACIL), _q(2, Difficulty.MEDIO), _q(3, Difficulty.DIFICIL),
        _q(4, Difficulty.MEDIO), _q(5, Difficulty.FACIL),
    ]
    total = 43 * 60
    sug = tiempos_sugeridos(preguntas, total)
    # Con redondeo por pregunta se admite un segundo de holgura por cada una.
    assert abs(sum(sug.values()) - total) <= len(preguntas)


def test_la_dificil_recibe_mas_tiempo_que_la_facil() -> None:
    preguntas = [_q(1, Difficulty.FACIL), _q(2, Difficulty.MEDIO), _q(3, Difficulty.DIFICIL)]
    sug = tiempos_sugeridos(preguntas, 3000)
    assert sug[1] < sug[2] < sug[3], "el tiempo tiene que crecer con la dificultad"


def test_en_lectora_la_primera_del_texto_carga_con_leerlo() -> None:
    """Las siguientes preguntas del mismo texto ya lo tienen leído: solo
    vuelven a mirarlo."""
    pasaje = ReadingPassage(title="T", body=" ".join(["palabra"] * 600), kind="no_literario")
    pasaje.id = 7
    preguntas = [
        _q(1, Difficulty.MEDIO, pasaje),
        _q(2, Difficulty.MEDIO, pasaje),
        _q(3, Difficulty.MEDIO, pasaje),
    ]
    sug = tiempos_sugeridos(preguntas, 3600)
    assert sug[1] > sug[2], "la que abre el texto tiene que costar más"
    assert sug[2] == sug[3], "las que siguen son iguales entre sí"


def test_un_texto_mas_largo_pide_mas_tiempo() -> None:
    """600 palabras y 200 palabras no se leen en el mismo rato."""
    def primera(palabras: int) -> int:
        pasaje = ReadingPassage(title="T", body=" ".join(["x"] * palabras), kind="no_literario")
        pasaje.id = 9
        qs = [_q(1, Difficulty.MEDIO, pasaje), _q(2, Difficulty.MEDIO, pasaje)]
        return tiempos_sugeridos(qs, 3600)[1]

    assert primera(600) > primera(200)


def test_sin_preguntas_o_sin_tiempo_no_devuelve_nada() -> None:
    """Los estados vacíos no inventan un presupuesto."""
    assert tiempos_sugeridos([], 3600) == {}
    assert tiempos_sugeridos([_q(1, Difficulty.MEDIO)], 0) == {}
