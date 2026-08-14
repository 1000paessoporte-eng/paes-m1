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


def test_ciencias_usa_los_datos_oficiales():
    """80 preguntas, 75 puntuadas, 160 minutos (temario DEMRE)."""
    from paes_api.modules.exam_focus.scoring import SCORING_BY_SUBJECT

    s = SCORING_BY_SUBJECT[Subject.CIENCIAS]
    assert (s.preguntas_oficiales, s.preguntas_puntuadas, s.duracion_oficial_min) == (
        80,
        75,
        160,
    )
    assert round(scoring.segundos_por_pregunta(Subject.CIENCIAS) * 80 / 60) == 160


def test_tabla_de_ciencias_es_la_oficial():
    assert scoring.estimar_puntaje(0, 75, Subject.CIENCIAS) == 100
    assert scoring.estimar_puntaje(50, 75, Subject.CIENCIAS) == 632
    assert scoring.estimar_puntaje(75, 75, Subject.CIENCIAS) == 1000


def test_ciencias_ofrece_sus_tres_disciplinas():
    assert EJES_POR_PRUEBA[Subject.CIENCIAS] == {"biologia", "fisica", "quimica"}
    assert SUBJECT_INCLUDES[Subject.CIENCIAS] == [Subject.CIENCIAS]


def test_biologia_declarada_sin_banco_todavia():
    """Los nodos de Biología existen pero no tienen preguntas.

    Es deliberado: su contenido es factual y el verificador no puede
    comprobarlo. Si algún día se agregan, este test falla y hay que decidir
    conscientemente que se revisaron a mano.
    """
    from paes_api.seed_data import QUESTIONS_CIENCIAS, SKILL_NODES_CIENCIAS

    bio = {n[0] for n in SKILL_NODES_CIENCIAS if n[2] == "biologia"}
    assert bio, "deberían existir nodos de biología"
    assert not [q for q in QUESTIONS_CIENCIAS if q["skill_node"] in bio]
