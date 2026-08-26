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


# Cuántas preguntas de biología se revisaron a mano, por nodo.
#
# Biología es el único eje donde la respuesta no siempre sale de un cálculo,
# así que el verificador no alcanza a cubrirlo solo. Este conteo es el
# reemplazo del tripwire anterior —que exigía CERO preguntas— y cumple la
# misma función: si alguien agrega una pregunta nueva, el test falla y obliga
# a declarar explícitamente que se revisó antes de que la vea un estudiante.
#
# Para subir un número acá hay que haber leído la pregunta completa.
BIOLOGIA_REVISADAS = {
    "cie_celula": 26,
    "cie_genetica": 26,
    "cie_ecosistemas": 26,
}


def test_biologia_solo_trae_preguntas_revisadas():
    """El banco de biología coincide con lo que se revisó a mano."""
    from collections import Counter

    from paes_api.seed_data import QUESTIONS_CIENCIAS, SKILL_NODES_CIENCIAS

    bio = {n[0] for n in SKILL_NODES_CIENCIAS if n[2] == "biologia"}
    assert bio == set(BIOLOGIA_REVISADAS), "cambió el conjunto de nodos de biología"

    real = Counter(q["skill_node"] for q in QUESTIONS_CIENCIAS if q["skill_node"] in bio)
    assert dict(real) == BIOLOGIA_REVISADAS, (
        "el banco de biología no coincide con lo revisado a mano. "
        "Lee las preguntas nuevas y recién ahí actualiza BIOLOGIA_REVISADAS."
    )


def test_ciencias_no_deja_nodos_sin_practicar():
    """Ningún nodo de Ciencias queda con menos de 5 preguntas.

    Un nodo con dos preguntas es peor que no tenerlo: aparece practicable en
    el árbol y se agota al primer intento.
    """
    from collections import Counter

    from paes_api.seed_data import QUESTIONS_CIENCIAS, SKILL_NODES_CIENCIAS

    por_nodo = Counter(q["skill_node"] for q in QUESTIONS_CIENCIAS)
    flacos = sorted(n[0] for n in SKILL_NODES_CIENCIAS if por_nodo[n[0]] < 5)
    assert not flacos, f"nodos de Ciencias con menos de 5 preguntas: {flacos}"


def test_historia_usa_los_datos_oficiales():
    """65 preguntas, 60 puntuadas, 2 horas (temario DEMRE)."""
    from paes_api.modules.exam_focus.scoring import SCORING_BY_SUBJECT

    s = SCORING_BY_SUBJECT[Subject.HISTORIA]
    assert (s.preguntas_oficiales, s.preguntas_puntuadas, s.duracion_oficial_min) == (
        65,
        60,
        120,
    )
    assert round(scoring.segundos_por_pregunta(Subject.HISTORIA) * 65 / 60) == 120


def test_tabla_de_historia_es_la_oficial():
    assert scoring.estimar_puntaje(0, 60, Subject.HISTORIA) == 100
    assert scoring.estimar_puntaje(30, 60, Subject.HISTORIA) == 545
    assert scoring.estimar_puntaje(60, 60, Subject.HISTORIA) == 1000


def test_historia_ofrece_sus_tres_ejes():
    assert EJES_POR_PRUEBA[Subject.HISTORIA] == {"historia", "ciudadania", "economia"}
    assert SUBJECT_INCLUDES[Subject.HISTORIA] == [Subject.HISTORIA]


def test_las_cinco_pruebas_tienen_banco_propio():
    """Ninguna prueba comparte banco con otra, salvo M2 que incluye M1."""
    for s in Subject:
        assert s in SUBJECT_INCLUDES, f"{s} sin banco declarado"
        assert s in EJES_POR_PRUEBA, f"{s} sin ejes declarados"
    assert SUBJECT_INCLUDES[Subject.M2] == [Subject.M1, Subject.M2]


def test_historia_no_afirma_hechos_sin_fuente():
    """Toda pregunta de los ejes de historia y ciudadanía se apoya en una fuente.

    Es la regla que hace verificable este banco: la respuesta se comprueba
    contra una fuente que escribimos, no contra conocimiento histórico que
    ningún script puede validar. Las de economía son de cálculo y no la
    necesitan.

    La fuente puede ser un texto (`passage`) o una figura propia (`image_url`).
    El temario DEMRE pide trabajar con mapas, gráficos y tablas, y en esas
    preguntas la fuente ES el dibujo: vive en el repositorio, se revisa en el
    mismo pull request y viaja con la pregunta, igual que un texto. Lo que la
    regla prohíbe sigue prohibido: preguntar de memoria, sin nada que
    contrastar.
    """
    from paes_api.seed_data import QUESTIONS_HISTORIA, SKILL_NODES_HISTORIA

    ejes = {n[0]: n[2] for n in SKILL_NODES_HISTORIA}
    for q in QUESTIONS_HISTORIA:
        if ejes[q["skill_node"]] in ("historia", "ciudadania"):
            assert q.get("passage") or q.get("image_url"), (
                f"sin fuente: {q['stem'][:50]}"
            )


def test_cada_texto_de_lectora_sostiene_varias_preguntas():
    """En la prueba real un texto nunca trae una sola pregunta.

    Escribir un texto largo para preguntar una cosa desperdicia el minuto que
    el estudiante gastó leyéndolo, y en un ensayo corto además desbalancea el
    tiempo. Tres es el piso.
    """
    from collections import Counter

    from paes_api.seed_data import PASSAGES, QUESTIONS_LECTORA

    por_texto = Counter(q["passage"] for q in QUESTIONS_LECTORA)
    for p in PASSAGES:
        assert por_texto[p["key"]] >= 3, (
            f"el texto '{p['key']}' tiene {por_texto[p['key']]} pregunta(s)"
        )


def test_lectora_cubre_sus_tres_habilidades_en_cada_dificultad():
    """El ensayo mezcla dificultades; si un eje solo tiene preguntas fáciles,
    el alumno que lo domina nunca encuentra dónde equivocarse."""
    from paes_api.seed_data import QUESTIONS_LECTORA

    ejes = {q["skill_node"] for q in QUESTIONS_LECTORA}
    assert ejes == {"lec_localizar", "lec_interpretar", "lec_evaluar"}
    for eje in ejes:
        dificultades = {q["difficulty"] for q in QUESTIONS_LECTORA if q["skill_node"] == eje}
        assert len(dificultades) >= 2, f"{eje} solo tiene preguntas {dificultades}"


def test_las_figuras_de_las_preguntas_existen_y_estan_descritas():
    """Toda figura referida por una pregunta existe y tiene texto alternativo.

    Una `image_url` mal escrita no rompe nada en el servidor: la pregunta se
    siembra igual y el alumno se encuentra con un recuadro vacío en pleno
    ensayo, sin forma de contestar. Y una figura sin descripción es una
    pregunta que no se puede rendir con lector de pantalla.

    Las dos mitades viven en el repositorio del frontend --el archivo en
    `public/preguntas/` y la descripción en `lib/figuras.ts`--, así que esto se
    puede comprobar sin base de datos ni navegador.
    """
    from pathlib import Path

    from paes_api.seed_data import (
        QUESTIONS,
        QUESTIONS_CIENCIAS,
        QUESTIONS_HISTORIA,
        QUESTIONS_LECTORA,
    )

    web = Path(__file__).resolve().parents[3] / "apps" / "web"
    descripciones = (web / "lib" / "figuras.ts").read_text(encoding="utf-8")

    todas = QUESTIONS + QUESTIONS_LECTORA + QUESTIONS_CIENCIAS + QUESTIONS_HISTORIA
    con_figura = [q for q in todas if q.get("image_url")]
    assert con_figura, "el banco ya no tiene ninguna pregunta con figura"

    for q in con_figura:
        ruta = q["image_url"]
        assert ruta.startswith("/preguntas/"), (
            f"{ruta}: las figuras van en /preguntas/, servidas desde public/"
        )
        archivo = web / "public" / ruta.lstrip("/")
        assert archivo.is_file(), f"falta el archivo de la figura: {ruta}"
        assert f'"{ruta}"' in descripciones, (
            f"{ruta} no tiene texto alternativo en apps/web/lib/figuras.ts"
        )

    # Una figura por pregunta. Un ensayo saca preguntas al azar del banco, así
    # que dos preguntas que compartan dibujo se le pueden repetir al mismo
    # alumno en dos ensayos seguidos, y lo que recuerda de una prueba a otra es
    # justamente la imagen.
    rutas = [q["image_url"] for q in con_figura]
    repetidas = {r for r in rutas if rutas.count(r) > 1}
    assert not repetidas, f"figuras usadas por más de una pregunta: {sorted(repetidas)}"
