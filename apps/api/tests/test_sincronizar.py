"""El sincronizador repara una pregunta sin hacerla desaparecer.

Estos tests cubren la decision, no el SQL: `planificar_alternativas` recibe lo
que hay en la base y lo que dice seed_data, y responde que corregir, que borrar
y que insertar. Es la parte donde estaba el defecto que motivo el cambio.

Hasta el 2026-08-23 publicar un cambio de alternativas significaba BORRAR la
pregunta y reponerla en una segunda pasada de seed.py. Entre las dos pasadas el
sitio quedaba con el banco incompleto —el 2026-08-19 M1 se vio en 991 de 1088—
y la pregunta volvia con otro id, asi que los ensayos ya rendidos la perdian.
Lo que estos tests fijan es que eso no puede volver a pasar: las filas que
siguen valiendo conservan su id.
"""

import importlib.util
from pathlib import Path

import pytest

_ruta = Path(__file__).resolve().parents[1] / "scripts" / "sincronizar.py"
_spec = importlib.util.spec_from_file_location("sincronizar", _ruta)
sincronizar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sincronizar)

planificar_alternativas = sincronizar.planificar_alternativas


def _deseada(texto, correcta=False, justificacion="porque si"):
    return {
        "text": texto,
        "is_correct": correcta,
        "justification": None if correcta else justificacion,
    }


def _actuales():
    """Cuatro alternativas como las devuelve la base: (id, label, texto, ok, justif)."""
    return [
        (10, "A", "12", False, "sumo en vez de multiplicar"),
        (11, "B", "24", True, None),
        (12, "C", "36", False, "multiplico de mas"),
        (13, "D", "48", False, "duplico el resultado"),
    ]


def _deseadas():
    return [
        _deseada("12", justificacion="sumo en vez de multiplicar"),
        _deseada("24", correcta=True),
        _deseada("36", justificacion="multiplico de mas"),
        _deseada("48", justificacion="duplico el resultado"),
    ]


def test_sin_cambios_no_toca_nada():
    corregir, borrar, insertar = planificar_alternativas(_actuales(), _deseadas())
    assert (corregir, borrar, insertar) == ([], [], [])


def test_un_distractor_reemplazado_conserva_las_otras_tres_filas():
    """El corazon del arreglo: cambiar UNA alternativa no borra la pregunta.

    Antes esto se publicaba borrando la pregunta entera y reponiendola con id
    nuevo. Aqui se comprueba que solo se va la fila que dejo de existir.
    """
    deseadas = _deseadas()
    deseadas[2] = _deseada("30", justificacion="olvido dividir por dos")

    corregir, borrar, insertar = planificar_alternativas(_actuales(), deseadas)

    assert borrar == [12]
    assert insertar == [("C", "30", False, "olvido dividir por dos")]
    assert corregir == []


def test_la_etiqueta_que_queda_libre_es_la_que_ocupa_la_nueva():
    """Las cuatro etiquetas siguen siendo A-D y ninguna se repite."""
    deseadas = _deseadas()
    deseadas[0] = _deseada("9", justificacion="resto en vez de sumar")

    _corregir, borrar, insertar = planificar_alternativas(_actuales(), deseadas)

    sobreviven = {a[1] for a in _actuales() if a[0] not in borrar}
    etiquetas = sobreviven | {i[0] for i in insertar}
    assert etiquetas == {"A", "B", "C", "D"}
    assert len(etiquetas) == 4


def test_corregir_una_justificacion_no_borra_ni_inserta():
    """El caso que NUNCA llegaba a produccion.

    seed.py salta la pregunta porque el enunciado ya existe, y el sync viejo
    solo miraba texto y marca de correcta: una justificacion reescrita se
    quedaba para siempre en el repositorio. Y es lo que el alumno lee en la
    autopsia del error.
    """
    deseadas = _deseadas()
    deseadas[0] = _deseada("12", justificacion="conto los objetos, no los pares")

    corregir, borrar, insertar = planificar_alternativas(_actuales(), deseadas)

    assert corregir == [(10, False, "conto los objetos, no los pares")]
    assert (borrar, insertar) == ([], [])


def test_mover_la_marca_de_correcta_no_borra_filas():
    """Si la correcta pasa a ser otra de las mismas cuatro, se corrige en su lugar."""
    deseadas = [
        _deseada("12", justificacion="sumo en vez de multiplicar"),
        _deseada("24", justificacion="se quedo con el subtotal"),
        _deseada("36", correcta=True),
        _deseada("48", justificacion="duplico el resultado"),
    ]

    corregir, borrar, insertar = planificar_alternativas(_actuales(), deseadas)

    assert sorted(corregir) == [
        (11, False, "se quedo con el subtotal"),
        (12, True, None),
    ]
    assert (borrar, insertar) == ([], [])


def test_nunca_reescribe_el_texto_de_una_fila_viva():
    """Garantia de historial: una respuesta rendida apunta a un id de alternativa.

    Reescribir el texto de esa fila saldria mas barato que borrarla e insertar
    otra, pero haria que un intento del mes pasado afirme que el alumno eligio
    algo que nunca vio. Se comprueba que toda fila que sobrevive conserva un
    texto que sigue estando en seed_data.
    """
    deseadas = [
        _deseada("100", justificacion="uno"),
        _deseada("200", correcta=True),
        _deseada("300", justificacion="tres"),
        _deseada("400", justificacion="cuatro"),
    ]

    corregir, borrar, _insertar = planificar_alternativas(_actuales(), deseadas)

    # No queda ninguna fila vieja: los cuatro textos cambiaron.
    assert sorted(borrar) == [10, 11, 12, 13]
    assert corregir == []


def test_reclama_si_no_alcanzan_las_etiquetas():
    """Las etiquetas son A-E y no hay una sexta: se falla en vez de inventarla.

    `alternatives.label` es un solo caracter. Sin este control, una pregunta
    con seis alternativas se insertaba con la etiqueta vacia o repetida y el
    problema recien se veia en pantalla.
    """
    deseadas = [_deseada(str(n)) for n in range(100, 106)]
    with pytest.raises(ValueError, match="no alcanzan las etiquetas"):
        planificar_alternativas([], deseadas)


def test_estado_deseado_indexa_por_enunciado_y_trae_el_texto_base():
    pregunta = {
        "stem": "¿Cuanto es 6 x 4?",
        "skill_node": "num_operatoria",
        "difficulty": "facil",
        "explanation": "Se multiplica.",
        "passage": "clave_del_texto",
        "alternatives": [
            {"text": "24", "is_correct": True, "justification": None},
            {"text": "10", "is_correct": False, "justification": "sumo"},
        ],
    }
    deseado = sincronizar.estado_deseado(
        [pregunta], {"clave_del_texto": "El titulo del texto"}
    )

    assert deseado["¿Cuanto es 6 x 4?"]["dificultad"] == "FACIL"
    assert deseado["¿Cuanto es 6 x 4?"]["texto_base"] == "El titulo del texto"
    assert len(deseado["¿Cuanto es 6 x 4?"]["alternativas"]) == 2


def test_una_pregunta_de_matematica_no_tiene_texto_base():
    pregunta = {
        "stem": "¿Cuanto es 2 + 2?",
        "skill_node": "num_operatoria",
        "difficulty": "facil",
        "explanation": "Se suma.",
        "alternatives": [{"text": "4", "is_correct": True, "justification": None}],
    }
    deseado = sincronizar.estado_deseado([pregunta], {})
    assert deseado["¿Cuanto es 2 + 2?"]["texto_base"] is None
