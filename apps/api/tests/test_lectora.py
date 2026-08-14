"""Competencia Lectora: la prueba se comporta distinto de matemática.

Lo que estos tests protegen es que un ensayo de lectura llegue con su texto.
Una pregunta de comprensión sin el texto al lado no se puede responder, y ese
es justamente el tipo de regresión que no se ve mirando el código.
"""

from paes_api.modules.exam_focus import scoring
from paes_api.modules.exam_focus.service import EJES_POR_PRUEBA, SUBJECT_INCLUDES
from paes_api.modules.skill_tree.models import Subject


def test_lectora_no_comparte_banco_con_matematica():
    assert SUBJECT_INCLUDES[Subject.LECTORA] == [Subject.LECTORA]
    assert Subject.LECTORA not in SUBJECT_INCLUDES[Subject.M2]


def test_lectora_ofrece_solo_sus_habilidades():
    assert EJES_POR_PRUEBA[Subject.LECTORA] == {"localizar", "interpretar", "evaluar"}
    assert "numeros" not in EJES_POR_PRUEBA[Subject.LECTORA]
    assert "localizar" not in EJES_POR_PRUEBA[Subject.M1]


def test_duracion_coincide_con_la_prueba_oficial():
    """65 preguntas en 150 minutos, según el temario DEMRE."""
    segundos = scoring.segundos_por_pregunta(Subject.LECTORA)
    assert round(segundos * 65 / 60) == 150


def test_tabla_de_puntaje_es_la_oficial():
    # Valores publicados por el DEMRE para el proceso 2026.
    assert scoring.estimar_puntaje(0, 60, Subject.LECTORA) == 100
    assert scoring.estimar_puntaje(30, 60, Subject.LECTORA) == 576
    assert scoring.estimar_puntaje(60, 60, Subject.LECTORA) == 1000


def test_toda_pregunta_de_lectora_trae_su_texto():
    from paes_api.seed_data import PASSAGES, QUESTIONS_LECTORA

    claves = {p["key"] for p in PASSAGES}
    for q in QUESTIONS_LECTORA:
        assert q.get("passage"), f"sin texto: {q['stem'][:50]}"
        assert q["passage"] in claves, f"texto inexistente: {q['passage']}"


def test_las_preguntas_de_matematica_no_llevan_texto():
    from paes_api.seed_data import QUESTIONS

    assert all("passage" not in q for q in QUESTIONS)
