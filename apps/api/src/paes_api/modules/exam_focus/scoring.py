"""Conversión de respuestas correctas a puntaje PAES estimado.

La PAES entrega un puntaje en escala 100-1000. La conversión desde el número
de respuestas correctas NO es lineal: se construye a partir de promedios de
habilidades y se equipara entre las distintas formas de la prueba.

Los valores de abajo son REFERENCIALES, basados en tablas publicadas por el
DEMRE para procesos recientes. El puntaje real depende de la forma rendida y
del proceso de admisión, por lo que la app siempre presenta este número como
"puntaje estimado". Cada prueba PAES tiene su propia tabla y su propia razón
tiempo/preguntas — por eso todo está parametrizado por `Subject`.
"""

from dataclasses import dataclass

from paes_api.modules.skill_tree.models import Subject

# Tabla oficial DEMRE, PAES Regular M1 (Admisión 2027). 65 preguntas, de las
# cuales 60 puntúan (5 son de pilotaje). Por eso la tabla va de 0 a 60.
_TABLA_M1: list[int] = [
    100, 134, 164, 192, 217, 240, 260, 280, 298, 316,  # 0-9
    334, 350, 364, 377, 388, 401, 416, 432, 446, 458,  # 10-19
    467, 475, 483, 494, 506, 521, 535, 548, 557, 564,  # 20-29
    571, 578, 588, 600, 614, 628, 641, 652, 660, 667,  # 30-39
    675, 685, 698, 713, 728, 740, 752, 762, 774, 786,  # 40-49
    802, 819, 836, 852, 868, 885, 904, 926, 949, 974,  # 50-59
    1000,  # 60
]

# Tabla oficial DEMRE, PAES de Invierno M2 (Proceso 2025). 55 preguntas
# oficiales (temario Admisión 2026), de las cuales 49 puntuaron en esta
# aplicación (el resto fueron de pilotaje). Fuente: demre.cl/paes/
# factores-seleccion/tabla-transformacion-puntajes-paes-invierno-p2025-m2
_TABLA_M2: list[int] = [
    100, 181, 212, 240, 265, 287, 308, 327, 347, 365,  # 0-9
    381, 396, 409, 424, 439, 455, 469, 481, 491, 502,  # 10-19
    514, 528, 542, 556, 567, 577, 586, 596, 609, 623,  # 20-29
    637, 651, 662, 672, 683, 695, 710, 725, 740, 755,  # 30-39
    768, 783, 800, 818, 837, 856, 877, 900, 926,       # 40-48
    1000,  # 49
]


# Tabla oficial DEMRE, PAES Regular de Competencia Lectora (Proceso 2026).
# 60 preguntas puntuadas de 65. Índice = respuestas correctas.
# https://demre.cl/paes/factores-seleccion/tabla-transformacion-puntajes-paes-regular-p2026-competencia-lectora
_TABLA_LECTORA: list[int] = [
    100, 159, 184, 206, 228, 249, 267, 284, 299, 316,
    333, 350, 364, 376, 387, 397, 410, 424, 440, 455,
    467, 477, 484, 492, 500, 511, 525, 540, 555, 567,
    576, 583, 590, 597, 607, 619, 634, 650, 663, 674,
    682, 690, 699, 710, 725, 740, 756, 770, 782, 794,
    808, 823, 841, 860, 878, 896, 916, 938, 963, 989,
    1000,
]


# Tabla oficial DEMRE, PAES Regular de Ciencias (Proceso 2026). 75 preguntas
# puntuadas de 80. Índice = respuestas correctas.
# https://demre.cl/paes/factores-seleccion/tabla-transformacion-puntajes-paes-regular-p2026-ciencias
_TABLA_CIENCIAS: list[int] = [
    100, 116, 140, 163, 183, 202, 220, 235, 249, 263,
    278, 293, 307, 318, 327, 335, 345, 356, 368, 381,
    393, 402, 410, 415, 420, 427, 435, 446, 458, 471,
    481, 489, 495, 499, 503, 507, 513, 522, 532, 545,
    557, 567, 574, 580, 584, 588, 593, 599, 608, 619,
    632, 644, 654, 662, 668, 673, 679, 688, 698, 711,
    724, 736, 747, 756, 765, 776, 789, 804, 819, 834,
    849, 866, 884, 905, 927, 1000,
]


# Tabla oficial DEMRE, PAES Regular de Historia y Cs. Sociales (Proceso 2026).
# 60 preguntas puntuadas de 65. Índice = respuestas correctas.
# https://demre.cl/paes/factores-seleccion/tabla-transformacion-puntajes-paes-regular-p2026-hycsoc
_TABLA_HISTORIA: list[int] = [
    100, 117, 145, 169, 191, 212, 233, 253, 270, 286,
    300, 314, 331, 348, 364, 377, 387, 397, 406, 418,
    432, 447, 463, 476, 486, 493, 500, 508, 517, 530,
    545, 561, 574, 585, 593, 600, 607, 616, 628, 643,
    659, 673, 686, 695, 705, 714, 727, 742, 759, 775,
    790, 804, 818, 835, 853, 874, 894, 915, 938, 964,
    1000,
]


@dataclass(frozen=True)
class SubjectScoring:
    """Parámetros de una prueba PAES: cuántas preguntas trae oficialmente,
    cuántas de esas puntúan, cuánto dura, y la tabla de conversión."""

    preguntas_oficiales: int
    preguntas_puntuadas: int
    duracion_oficial_min: int
    tabla: list[int]


SCORING_BY_SUBJECT: dict[Subject, SubjectScoring] = {
    Subject.M1: SubjectScoring(
        preguntas_oficiales=65,
        preguntas_puntuadas=60,
        duracion_oficial_min=140,
        tabla=_TABLA_M1,
    ),
    Subject.LECTORA: SubjectScoring(
        preguntas_oficiales=65,
        preguntas_puntuadas=60,
        duracion_oficial_min=150,
        tabla=_TABLA_LECTORA,
    ),
    Subject.CIENCIAS: SubjectScoring(
        preguntas_oficiales=80,
        preguntas_puntuadas=75,
        duracion_oficial_min=160,
        tabla=_TABLA_CIENCIAS,
    ),
    Subject.HISTORIA: SubjectScoring(
        preguntas_oficiales=65,
        preguntas_puntuadas=60,
        duracion_oficial_min=120,
        tabla=_TABLA_HISTORIA,
    ),
    Subject.M2: SubjectScoring(
        preguntas_oficiales=55,
        preguntas_puntuadas=49,
        duracion_oficial_min=140,
        tabla=_TABLA_M2,
    ),
}

# Compatibilidad hacia atrás: código existente que importaba estas constantes
# asumiendo M1 (nunca había otra prueba).
PREGUNTAS_OFICIALES = SCORING_BY_SUBJECT[Subject.M1].preguntas_oficiales
PREGUNTAS_PUNTUADAS = SCORING_BY_SUBJECT[Subject.M1].preguntas_puntuadas
DURACION_OFICIAL_MIN = SCORING_BY_SUBJECT[Subject.M1].duracion_oficial_min


def segundos_por_pregunta(subject: Subject = Subject.M1) -> float:
    """Ritmo oficial de la prueba: duración total / cantidad de preguntas."""
    s = SCORING_BY_SUBJECT[subject]
    return (s.duracion_oficial_min * 60) / s.preguntas_oficiales


def estimar_puntaje(correctas: int, total: int, subject: Subject = Subject.M1) -> int:
    """Estima el puntaje PAES de un ensayo de cualquier largo.

    Un ensayo de 20 preguntas no puede usar la tabla directamente (12 correctas
    de 20 no equivalen a 12 correctas del total puntuado). Se escala la
    proporción de aciertos a la base puntuada de la prueba y luego se
    interpola en su tabla.
    """
    if total <= 0:
        return 100

    s = SCORING_BY_SUBJECT[subject]
    proporcion = min(max(correctas / total, 0.0), 1.0)
    equivalente = proporcion * s.preguntas_puntuadas

    inferior = int(equivalente)
    superior = min(inferior + 1, s.preguntas_puntuadas)
    fraccion = equivalente - inferior

    puntaje = s.tabla[inferior] + (s.tabla[superior] - s.tabla[inferior]) * fraccion
    return round(puntaje)
