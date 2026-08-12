"""Conversión de respuestas correctas a puntaje PAES estimado.

La PAES entrega un puntaje en escala 100-1000. La conversión desde el número
de respuestas correctas NO es lineal: se construye a partir de promedios de
habilidades y se equipara entre las distintas formas de la prueba.

Los valores de abajo son REFERENCIALES, basados en tablas publicadas para
procesos recientes de la PAES Regular M1. El puntaje real depende de la forma
rendida y del proceso de admisión, por lo que la app siempre presenta este
número como "puntaje estimado".

La prueba oficial tiene 65 preguntas, de las cuales 60 puntúan (5 son de
pilotaje). Por eso la tabla va de 0 a 60.
"""

# Datos oficiales del temario DEMRE (Admisión 2027) para M1.
PREGUNTAS_OFICIALES = 65
PREGUNTAS_PUNTUADAS = 60
DURACION_OFICIAL_MIN = 140

#: Puntaje PAES para cada cantidad de respuestas correctas, de 0 a 60.
TABLA_M1: list[int] = [
    100, 134, 164, 192, 217, 240, 260, 280, 298, 316,  # 0-9
    334, 350, 364, 377, 388, 401, 416, 432, 446, 458,  # 10-19
    467, 475, 483, 494, 506, 521, 535, 548, 557, 564,  # 20-29
    571, 578, 588, 600, 614, 628, 641, 652, 660, 667,  # 30-39
    675, 685, 698, 713, 728, 740, 752, 762, 774, 786,  # 40-49
    802, 819, 836, 852, 868, 885, 904, 926, 949, 974,  # 50-59
    1000,  # 60
]


def segundos_por_pregunta() -> float:
    """Ritmo oficial: 140 min / 65 preguntas ≈ 2 min 9 s por pregunta."""
    return (DURACION_OFICIAL_MIN * 60) / PREGUNTAS_OFICIALES


def estimar_puntaje(correctas: int, total: int) -> int:
    """Estima el puntaje PAES de un ensayo de cualquier largo.

    Un ensayo de 20 preguntas no puede usar la tabla directamente (12 correctas
    de 20 no equivalen a 12 correctas de 60). Se escala la proporción de
    aciertos a la base de 60 preguntas y luego se interpola en la tabla.
    """
    if total <= 0:
        return 100

    proporcion = min(max(correctas / total, 0.0), 1.0)
    equivalente = proporcion * PREGUNTAS_PUNTUADAS

    inferior = int(equivalente)
    superior = min(inferior + 1, PREGUNTAS_PUNTUADAS)
    fraccion = equivalente - inferior

    puntaje = TABLA_M1[inferior] + (TABLA_M1[superior] - TABLA_M1[inferior]) * fraccion
    return round(puntaje)
