"""Controles de calidad del banco de preguntas antes de sembrarlo.

Dos capas:

1. Estructura: recorre TODAS las preguntas y verifica que cumplan el contrato
   que asume el resto del sistema (una sola correcta, tres distractores, nodo
   existente, enunciados únicos, distractores justificados y distintos entre
   sí, y que ni la explicación ni las justificaciones mencionen letras de
   alternativa, porque seed.py mezcla el orden).

2. Aritmética: recalcula desde cero el resultado de las preguntas de cálculo y
   lo compara con la alternativa marcada como correcta. Cada entrada de
   COMPROBACIONES es independiente del texto de la pregunta: si alguien edita
   un enunciado y se equivoca en el número, esto falla.

Uso:
    uv run python scripts/verificar_banco.py
"""

import re
import sys
from collections import Counter
from fractions import Fraction
from math import comb, factorial, isclose, sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from paes_api.seed_data import QUESTIONS, SKILL_NODES, SKILL_NODES_M2

CODIGOS = {n[0] for n in SKILL_NODES} | {n[0] for n in SKILL_NODES_M2}
DIFICULTADES = {"facil", "medio", "dificil"}

# Enunciado (recortado) -> valor esperado, recalculado acá de forma independiente.
COMPROBACIONES: dict[str, str] = {
    # --- racionales ---
    "5/6 − 2/9": str(Fraction(5, 6) - Fraction(2, 9)),
    "(3/5) × (10/9)": str(Fraction(3, 5) * Fraction(10, 9)),
    "2 + (1/2) ÷ (2/3)": str(2 + Fraction(1, 2) / Fraction(2, 3)),
    "tambor tiene 3/4": str(Fraction(3, 4) - Fraction(1, 3) * Fraction(3, 4)),
    "(2/3 − 1/4) ÷ (5/6 + 1/2)": str(
        (Fraction(2, 3) - Fraction(1, 4)) / (Fraction(5, 6) + Fraction(1, 2))
    ),
    "a = 2/5 y b = 3/4": str(
        (Fraction(2, 5) + Fraction(3, 4)) / (Fraction(3, 4) - Fraction(2, 5))
    ),
    # --- potencias y raíces ---
    "2³ · 2⁴": str(2**3 * 2**4),
    "√81 − √16": str(int(sqrt(81) - sqrt(16))),
    "(3⁵ · 3²) ÷ 3⁴": str(3**5 * 3**2 // 3**4),
    "5⁻²": str(Fraction(1, 5**2)),
    "2ˣ = 32": str(5 if 2**5 == 32 else None),
    # --- porcentajes ---
    "15% de 240": str(int(0.15 * 240)),
    "18.000 y se le aplica un descuento del 25%": f"{int(18000 * 0.75):,}".replace(",", "."),
    "40 estudiantes, 24 son mujeres": f"{int(24 / 40 * 100)}%",
    "sube un 20% y después baja un 20%": "4" if abs(1 - 1.2 * 0.8 - 0.04) < 1e-9 else "?",
    "Ocho trabajadores construyen": str(8 * 15 // 12),
    # --- álgebra ---
    "5a + 3b − 2a + 7b": f"{5 - 2}a + {3 + 7}b",
    "a + b = 9 y a · b = 20": str(9**2 - 2 * 20),
    "4x − 7 = 13": str((13 + 7) // 4),
    "3(x − 2) = 2x + 5": str(11 if 3 * (11 - 2) == 2 * 11 + 5 else None),
    "suma de tres números consecutivos es 72": str(72 // 3 + 1),
    "5x + 3 = 2x + 18": str((18 - 3) // (5 - 2)),
    "3x + 2y = 16 y 2x + 3y = 14": str((16 + 14) // 5),
    "3 kilos de manzanas y 2 de peras": f"${(4600 - 2600) // 2:,}".replace(",", "."),
    "f(x) = 3x − 4": str(3 * 6 - 4),
    "(1, 2) y (5, 10)": str((10 - 2) // (5 - 1)),
    "y = 2x − 6 corta al eje X": f"({6 // 2}, 0)",
    "vértice de la parábola y = x² − 6x + 5": f"({6 // 2}, {3**2 - 6 * 3 + 5})",
    "f(x) = 2x + b cumple f(3) = 11": str(11 - 2 * 3),
    # --- geometría ---
    "triángulo de base 12 cm y altura 7 cm": f"{12 * 7 // 2} cm²",
    "circunferencia tiene radio 5 cm": f"{3.14 * 5**2:.1f} cm²".replace(".", ","),
    "perímetro 36 cm y su largo mide 11 cm": f"{(36 // 2 - 11) * 11} cm²",
    "cuadrado de lado 10 cm tiene inscrito": f"{100 - 3.14 * 25:.1f} cm²".replace(".", ","),
    "rectángulo de 9 cm de largo y 4 cm de ancho": f"{2 * (9 + 4)} cm",
    "catetos miden 15 cm y 20 cm": f"{int(sqrt(15**2 + 20**2))} cm",
    "hipotenusa mide 25 cm y un cateto 7 cm": f"{int(sqrt(25**2 - 7**2))} cm",
    "poste de 8 m": f"{int(sqrt(8**2 + 15**2))} m",
    "catetos miden 3 cm y 4 cm": f"{3 * 4 // 2} cm²",
    "cubo de arista 4 cm": f"{4**3} cm³",
    "cilindro de radio 3 cm y altura 10 cm": f"{3.14 * 9 * 10:.1f} cm³".replace(".", ","),
    "5 cm de largo, 3 cm de ancho y 2 cm de alto": f"{2 * (5 * 3 + 5 * 2 + 3 * 2)} cm²",
    "cono tiene radio 6 cm y altura 10 cm": f"{3.14 * 36 * 10 / 3:.1f} cm³".replace(".", ","),
    "P(6, 1) se traslada": f"({6 - 4}, {1 - 3})",
    "P(−3, 4) se refleja respecto del eje Y": f"({3 + 2}, {4 - 1})",
    "P(3, −2) una homotecia": f"({3 * 4}, {-2 * 4})",
    "triángulo de área 12 cm² se somete": f"{12 * 3**2} cm²",
    "8 cm y su correspondiente en la imagen mide 20": str(20 / 8).replace(".", ","),
    "rectángulo de 5 cm por 8 cm se amplía": f"{2 * (5 + 8) * 3} cm",
    "ángulo de 30° y su hipotenusa mide 10 cm": f"{int(10 * 0.5)} cm",
    "sen α = 0,6": str(sqrt(1 - 0.6**2)).replace(".", ",")[:3],
    # --- estadística y probabilidad ---
    "promedio de los datos 4, 8, 10, 6 y 12": str((4 + 8 + 10 + 6 + 12) // 5),
    "mediana de los datos 7, 3, 9, 1 y 5": str(sorted([7, 3, 9, 1, 5])[2]),
    "promedio de cuatro números es 15": str(5 * 16 - 4 * 15),
    "rango del conjunto 12, 4, 19, 7 y 15": str(19 - 4),
    "3 estudiantes obtuvieron nota 6": str((3 * 6 + 2 * 4) / 5).replace(".", ","),
    "4 entradas y 5 platos de fondo": str(4 * 5),
    "ordenar 6 cuadros": str(factorial(6)),
    "3 cifras distintas": str(5 * 4 * 3),
    "6 personas se debe elegir un comité de 2": str(comb(6, 2)),
    "2 letras seguidas de 3 dígitos": f"{26**2 * 10**3:,}".replace(",", "."),
    "3 poleras y 4 pantalones": str(3 * 4),
    "número primo": str(Fraction(3, 6)),
    "7 fichas blancas y 5 negras": str(Fraction(5, 12)),
    "Se lanzan dos monedas. ¿Cuál": str(Fraction(1, 4)),
    "baraja de 52 cartas": f"{4 + 13 - 1}/52",
    "4 bolitas blancas y 6 negras": str(Fraction(4, 10) * Fraction(3, 9)),
    "llueva mañana es 0,3": str(round(1 - 0.3, 1)).replace(".", ","),
    "varianza del conjunto 2, 4, 6": str(Fraction(8, 3)),
    "el 60% practica deporte": str(round(0.24 / 0.6, 2)).replace(".", ",")[:3],
    "A y B son independientes, con P(A) = 0,5": str(0.5 * 0.3).replace(".", ","),
    "3 bolitas rojas y 2 verdes": str(Fraction(2, 4)),
    "6! dividido por 4!": str(factorial(6) // factorial(4)),
    "3 delegados de un grupo de 7": str(comb(7, 3)),
    "letras de la palabra CASA": str(factorial(4) // factorial(2)),
    "4 personas en una fila": str(factorial(3) * factorial(2)),
    "5 hombres y 4 mujeres": str(comb(5, 2) * comb(4, 1)),
    "moneda 4 veces": str(2**4),
    "moneda 3 veces": str(Fraction(3, 8)),
    "5 intentos y probabilidad de éxito 0,2": str(int(5 * 0.2)),
    "4 veces con probabilidad de éxito 0,5": str(comb(4, 3) * 0.5**4).replace(".", ","),
    # --- M2 números ---
    "racionalizar 6/√3": "2√3" if isclose(6 / sqrt(3), 2 * sqrt(3)) else "?",
    "(√5 + 2)(√5 − 2)": str(5 - 4),
    "|3 − 8| + |−4|": str(abs(3 - 8) + abs(-4)),
    "200.000 al 5% de interés simple": f"${int(200000 * 0.05):,}".replace(",", "."),
    "100.000 se invierte al 10% de interés compuesto": f"${int(100000 * 1.1**2):,}".replace(",", "."),
    "80.000 y se paga en 4 cuotas": f"${int(80000 * 1.2 / 4):,}".replace(",", "."),
    "500.000 genera": f"{int(60000 / (500000 * 2) * 100)}%",
    "sube un 10% y luego se le aplica un descuento del 10%": f"${int(50000 * 1.1 * 0.9):,}".replace(",", "."),
    "log₂ 32": str(5 if 2**5 == 32 else None),
    "log 100 + log 1.000": str(2 + 3),
    "log x = 3": f"{10**3:,}".replace(",", "."),
    "log₃ 81 − log₃ 9": str(4 - 2),
    "log₅ 1": "0",
    "¿cuál es el valor de f(−1)?": str((-1) ** 5),
    "f(x) = 2x⁴": str(2 * 2**4),
    "f(x) = ax³ y f(2) = 24": str(24 // 2**3),
    # ================= LOTE 4 — eje NÚMEROS =================
    # --- racionales ---
    "5/8 − 1/6": str(Fraction(5, 8) - Fraction(1, 6)),
    "jarra hay 7/8 de litro": str(Fraction(7, 8) - Fraction(1, 4)),
    "(3/4) ÷ (9/8)": str(Fraction(3, 4) / Fraction(9, 8)),
    "2/5 de una ruta": str(1 - (Fraction(2, 5) + Fraction(1, 3))),
    "x = 3/8 y y = 5/6": str(
        (Fraction(5, 6) - Fraction(3, 8)) / (Fraction(5, 6) + Fraction(3, 8))
    ),
    "(5/6 − 1/2) × (3/4 + 1/2)": str(
        (Fraction(5, 6) - Fraction(1, 2)) * (Fraction(3, 4) + Fraction(1, 2))
    ),
    # --- potencias y raíces ---
    "3² · 3³": str(3**2 * 3**3),
    "√169 + √36": str(int(sqrt(169) + sqrt(36))),
    "(5⁴ · 5²) ÷ 5³": str(5**4 * 5**2 // 5**3),
    "3⁻³": str(Fraction(1, 3**3)),
    "3ˣ = 81": str(4 if 3**4 == 81 else None),
    "√(3² + 4²) · √49": str(round(sqrt(3**2 + 4**2) * sqrt(49))),
    # --- porcentajes ---
    "35% de 480": str(int(0.35 * 480)),
    # round, no int: 24000 * 1.15 da 27599.999... en coma flotante y truncar bajaría a 27.599.
    "cuesta $24.000 y sube un 15%": f"{round(24000 * 1.15):,}".replace(",", "."),
    "45 estudiantes, 27 aprobaron": f"{int(27 / 45 * 100)}%",
    "descuentos sucesivos: 20% y luego 10%": f"{int(50000 * 0.8 * 0.9):,}".replace(",", "."),
    "Doce operarios pintan": str(12 * 10 // 8),
    "sube un 60% y luego baja un 25%": f"{round((1.6 * 0.75 - 1) * 100)}%",
    # --- números reales ---
    "√75 en su forma más simple": "5" if isclose(sqrt(75), 5 * sqrt(3)) else "?",
    "√58": f"{int(sqrt(58))} y {int(sqrt(58)) + 1}",
    "(√5 + √5)²": str(round((2 * sqrt(5)) ** 2)),
    "a = √12 y b = √27": "5" if isclose(sqrt(12) + sqrt(27), 5 * sqrt(3)) else "?",
    "racionalizar 10/√5": "2" if isclose(10 / sqrt(5), 2 * sqrt(5)) else "?",
    "|−9| − |4 − 11|": str(abs(-9) - abs(4 - 11)),
    # --- matemática financiera ---
    "$300.000 al 4% de interés simple": f"{int(300000 * 0.04 * 3):,}".replace(",", "."),
    "capital de $500.000 se invierte al 6%": f"{int(500000 * (1 + 0.06 * 2)):,}".replace(",", "."),
    "$120.000 se invierte al 5% compuesto": f"{int(120000 * 1.05**2):,}".replace(",", "."),
    "$80.000 al 5% anual en 2 años": str(
        round(80000 * 1.05**2 - 80000 - 80000 * 0.05 * 2)
    ),
    "$1.200.000 se paga en 12 cuotas": f"{1200000 // 12 * (12 - 5):,}".replace(",", "."),
    "3 cuotas de $16.500": f"{round((3 * 16500 - 45000) / 45000 * 100)}%",
    # --- logaritmos ---
    "log₂ 64": str(6 if 2**6 == 64 else None),
    "log 10.000": str(4 if 10**4 == 10000 else None),
    "Si log x = 2": str(10**2),
    "log₃ 9 + log₂ 8": str(2 + 3),
    "log 2 ≈ 0,301": f"{3 * 0.301:.3f}".replace(".", ","),
    # Con base 5 el enunciado contendría "log₅ 125", que arrastra el fragmento
    # "log₅ 1" de otra comprobación y lo dejaría calzando con dos preguntas.
    "log₂ 128 − log₂ 8": str(7 - 3),
    # ================= LOTE 5 — eje ÁLGEBRA =================
    # --- expresiones algebraicas ---
    "reducir 7x − 3x + 2x": f"{7 - 3 + 2}x",
    "reducir 6m + 4n − 2m − 9n": f"{6 - 2}m − {9 - 4}n",
    "(x + 5)²": f"x² + {2 * 5}x + {5**2}",
    "(x − 3)²": f"x² − {2 * 3}x + {3**2}",
    "(x + 6)(x − 6)": f"x² − {6**2}",
    "factorización de x² − 64": f"(x + {int(sqrt(64))})(x − {int(sqrt(64))})",
    "factorización de 4x² + 8x": f"4x(x + {8 // 4})",
    "reducir 2(4x + 3) − 5x": f"{2 * 4 - 5}x + {2 * 3}",
    "factorización de x² + 9x + 20": "(x + 4)(x + 5)" if 4 * 5 == 20 and 4 + 5 == 9 else "?",
    "factorización de x² − 3x − 10": "(x − 5)(x + 2)" if -5 * 2 == -10 and -5 + 2 == -3 else "?",
    "(x² − 36)/(x − 6)": f"x + {int(sqrt(36))}",
    "(3x + 6)/(x + 2)": str(6 // 2),
    "(x + 2)(x + 7)": f"x² + {2 + 7}x + {2 * 7}",
    "3x² − 4x + 1": str(3 * (-2) ** 2 - 4 * (-2) + 1),
    "5(2a − 3) − 3(a − 4)": f"{5 * 2 - 3}a − {5 * 3 - 3 * 4}",
    "2x² − 18": f"2(x + {int(sqrt(9))})(x − {int(sqrt(9))})",
    "a + b = 7 y ab = 12": str(7**2 - 2 * 12),
    "a − b = 5 y ab = 6": str(5**2 + 2 * 6),
    "(x² + 5x + 6)/(x + 2)": f"x + {6 // 2}",
    "(x² − 4)/(x² + 4x + 4)": f"(x − {2})/(x + {2})",
    "reducir 8y − y + 3y": f"{8 - 1 + 3}y",
    "reducir 3a + 7b − a − 2b": f"{3 - 1}a + {7 - 2}b",
    "(x + 1)(x + 9)": f"x² + {1 + 9}x + {1 * 9}",
    "(2x + 3)²": f"{2**2}x² + {2 * 2 * 3}x + {3**2}",
    "factorización de x² − 100": f"(x + {int(sqrt(100))})(x − {int(sqrt(100))})",
    "factorización de 5x² − 15x": f"5x(x − {15 // 5})",
    "doble de un número aumentado en 7": f"2n + {7}",
    "reducir 4(x − 2) + 3x": f"{4 + 3}x − {4 * 2}",
    "factorización de x² + 11x + 30": "(x + 5)(x + 6)" if 5 * 6 == 30 and 5 + 6 == 11 else "?",
    "factorización de x² − 8x + 15": "(x − 3)(x − 5)" if 3 * 5 == 15 and 3 + 5 == 8 else "?",
    "factorización de x² + 2x − 24": "(x + 6)(x − 4)" if 6 * -4 == -24 and 6 - 4 == 2 else "?",
    "(x² − 25)/(x + 5)": f"x − {int(sqrt(25))}",
    "(4x + 12)/(x + 3)": str(12 // 3),
    "2x² − 5x + 4": str(2 * 3**2 - 5 * 3 + 4),
    "3(2m + 5) − 2(m − 1)": f"{3 * 2 - 2}m + {3 * 5 + 2}",
    "(3x − 2)(3x + 2)": f"{3**2}x² − {2**2}",
    "largo (x + 5) y ancho (x − 2)": f"{2 * 2}x + {2 * (5 - 2)}",
    "a + b = 10 y ab = 21": str(10**2 - 2 * 21),
    "(x² − 7x + 12)/(x − 3)": f"x − {12 // 3}",
    "factorización completa de 3x² − 27": f"3(x + {int(sqrt(9))})(x − {int(sqrt(9))})",
    "(x² + 6x + 9)/(x² − 9)": f"(x + {3})/(x − {3})",
    # --- ecuaciones e inecuaciones lineales ---
    "3x + 4 = 19": str((19 - 4) // 3),
    "5x − 8 = 12": str((12 + 8) // 5),
    "x/4 + 3 = 8": str((8 - 3) * 4),
    "2x + 9 = 3x − 1": str(9 + 1),
    "inecuación x + 5 > 12": f"x > {12 - 5}",
    "inecuación 4x ≤ 20": f"x ≤ {20 // 4}",
    "7 − x = 2": str(7 - 2),
    "6x = 4x + 14": str(14 // (6 - 4)),
    "4(x + 3) = 2x + 20": str((20 - 4 * 3) // (4 - 2)),
    "5(x − 1) = 3(x + 3)": str((3 * 3 + 5 * 1) // (5 - 3)),
    "inecuación −4x + 2 < 14": f"x > {(14 - 2) // -4}",
    "inecuación 5x − 3 ≥ 2x + 9": f"x ≥ {(9 + 3) // (5 - 2)}",
    "x/2 + x/3 = 5": str(int(5 / (Fraction(1, 2) + Fraction(1, 3)))),
    "doble de un número disminuido en 5 es 19": str((19 + 5) // 2),
    "suma de dos números consecutivos es 47": str((47 - 1) // 2),
    "3(2x − 1) = 4x + 7": str((7 + 3) // (6 - 4)),
    "(x + 2)/3 = (x − 4)/2": str((3 * 4 + 2 * 2) // (3 - 2)),
    "padre tiene 40 años y su hijo 10": str(40 - 2 * 10),
    "inecuación 2(x − 3) > 3(x + 1)": f"x < {-(3 + 2 * 3)}",
    "número aumentado en su mitad": str(int(27 / (1 + Fraction(1, 2)))),
    "2x − 7 = 9": str((9 + 7) // 2),
    "8 + 3x = 23": str((23 - 8) // 3),
    "x/5 = 7": str(7 * 5),
    "9x = 5x + 24": str(24 // (9 - 5)),
    "inecuación x − 4 ≥ 6": f"x ≥ {6 + 4}",
    "inecuación 3x < 21": f"x < {21 // 3}",
    "10 − 2x = 4": str((10 - 4) // 2),
    "6(x − 2) = 3x + 6": str((6 + 6 * 2) // (6 - 3)),
    "2(x + 4) + 3 = 5x − 4": str((2 * 4 + 3 + 4) // (5 - 2)),
    "inecuación −2x ≥ 10": f"x ≤ {10 // -2}",
    "inecuación 4(x + 1) < 2x + 10": f"x < {(10 - 4) // (4 - 2)}",
    "x/3 − x/6 = 2": str(int(2 / (Fraction(1, 3) - Fraction(1, 6)))),
    "triple de un número aumentado en 4": str((25 - 4) // 3),
    "dos números pares consecutivos es 66": str((66 - 2) // 2),
    "3x + 2y = 12 e y = 3": str((12 - 2 * 3) // 3),
    "(2x − 1)/4 = (x + 3)/3": f"{(4 * 3 + 3 * 1) / (3 * 2 - 4):.1f}".replace(".", ","),
    "triple de la edad de Beto": str(48 // (3 + 1)),
    "inecuación (x + 5)/2 ≤ x − 1": f"x ≥ {5 + 2}",
    "número más su tercera parte": str(int(32 / (1 + Fraction(1, 3)))),
    "5(x − 2) − 3(x + 1) = 7": str((7 + 5 * 2 + 3) // (5 - 3)),
    "al doble de un número se le resta 9": str(9 + 4),
    # --- sistemas 2x2 ---
    "x + y = 9 ; x − y = 3": f"x = {(9 + 3) // 2}, y = {(9 - 3) // 2}",
    "x + y = 20 ; x = 3y": f"x = {3 * (20 // 4)}, y = {20 // 4}",
    "x + y = 8 ; 2x + y = 13": f"x = {13 - 8}, y = {8 - (13 - 8)}",
    "y = 2x ; x + y = 15": f"x = {15 // 3}, y = {2 * (15 // 3)}",
    "suma de dos números es 24 y su diferencia es 6": f"{(24 + 6) // 2} y {(24 - 6) // 2}",
    "3x + y = 14 ; x + y = 6": f"x = {(14 - 6) // 2}, y = {6 - (14 - 6) // 2}",
    "2x + 3y = 16 ; x − y = 3": f"x = {(16 + 3 * 3) // 5}, y = {(16 - 2 * 3) // 5}",
    "4x − y = 10 ; 2x + y = 8": f"x = {(10 + 8) // 6}, y = {8 - 2 * ((10 + 8) // 6)}",
    "x + 2y = 11 ; 3x − 2y = 9": f"x = {(11 + 9) // 4}, y = {(11 - (11 + 9) // 4) // 2}",
    "2 cuadernos y 3 lápices": f"${2400 - 2 * 500:,}".replace(",", "."),
    "5x + 2y = 24 ; 3x − 2y = 8": f"x = {(24 + 8) // 8}, y = {(24 - 5 * ((24 + 8) // 8)) // 2}",
    "20 vehículos y 70 ruedas": str((70 - 2 * 20) // 2),
    "6x + y = 20 ; 2x + y = 8": f"x = {(20 - 8) // 4}, y = {8 - 2 * ((20 - 8) // 4)}",
    "x − y = 5 ; x + y = 11": f"x = {(11 + 5) // 2}, y = {(11 - 5) // 2}",
    "3x + 2y = 19 ; 2x + 3y = 16": f"x = {(3 * 19 - 2 * 16) // 5}, y = {(3 * 16 - 2 * 19) // 5}",
    "x/2 + y = 7 ; x + y = 10": f"x = {2 * (10 - 7)}, y = {10 - 2 * (10 - 7)}",
    "mayor excede al menor en 8 y su suma es 34": f"{(34 + 8) // 2} y {(34 - 8) // 2}",
    "4x + 3y = 27 ; 2x − y = 1": f"x = {(27 + 3) // 10}, y = {2 * ((27 + 3) // 10) - 1}",
    "Se vendieron 40 entradas": str((164000 - 3000 * 40) // (5000 - 3000)),
    "x + y = 14 y x − 2y = 2": str(14 - 2 * ((14 - 2) // 3)),
    "2x + y = 9 y x + 2y = 9": str((9 + 9) // 3),
    "x + y = 12 ; y = x + 4": f"x = {(12 - 4) // 2}, y = {(12 + 4) // 2}",
    "2x + y = 10 ; y = 4": f"x = {(10 - 4) // 2}, y = 4",
    "x + y = 30 ; x − y = 10": f"x = {(30 + 10) // 2}, y = {(30 - 10) // 2}",
    "y = x − 3 ; x + y = 17": f"x = {(17 + 3) // 2}, y = {(17 - 3) // 2}",
    "3x = y ; x + y = 16": f"x = {16 // 4}, y = {3 * (16 // 4)}",
    "2x − y = 7 ; x + y = 8": f"x = {(7 + 8) // 3}, y = {8 - (7 + 8) // 3}",
    "3x + 4y = 26 ; x − 2y = 2": f"x = {(26 + 2 * 2) // 5}, y = {(26 - 3 * 2) // 10}",
    "5x − 2y = 11 ; 3x + 2y = 13": f"x = {(11 + 13) // 8}, y = {(13 - 3 * ((11 + 13) // 8)) // 2}",
    "x + 3y = 14 ; 2x − 3y = 1": f"x = {(14 + 1) // 3}, y = {(14 - (14 + 1) // 3) // 3}",
    "2 kilos de pan y 3 litros de leche": f"${6500 - 2 * 2700:,}".replace(",", "."),
    "4x + y = 17 ; 2x + y = 11": f"x = {(17 - 11) // 2}, y = {11 - 2 * ((17 - 11) // 2)}",
    "25 cabezas y 80 patas": str((4 * 25 - 80) // 2),
    "2x + 3y = 17 ; 5x − 2y = 14": f"x = {(2 * 17 + 3 * 14) // 19}, y = {(5 * 17 - 2 * 14) // 19}",
    "x/3 + y = 5 ; x + y = 9": f"x = {9 - (3 * 5 - 9) // 2}, y = {(3 * 5 - 9) // 2}",
    "suma de dos números es 40 y uno de ellos es 4 veces": f"{4 * (40 // 5)} y {40 // 5}",
    "5x + 3y = 29 ; 2x − y = 5": f"x = {(29 + 3 * 5) // 11}, y = {2 * ((29 + 15) // 11) - 5}",
    "3 entradas de adulto y 2 de niño": f"${3 * 7000 - 19000:,}".replace(",", "."),
    "x · y si x + y = 9 y x − y = 1": str(((9 + 1) // 2) * ((9 - 1) // 2)),
    "3x + y = 11 y x + 3y = 9": str((11 + 9) // 4),
    "x + y = 18 ; x = y + 6": f"x = {(18 + 6) // 2}, y = {(18 - 6) // 2}",
}


def _norm(t: str) -> str:
    """Normaliza para comparar: el banco usa el signo menos U+2212, no el guion."""
    return t.replace("\u2212", "-").replace("\u00a0", " ").strip()


def main() -> int:
    fallas: list[str] = []

    # ---- capa 1: estructura ----
    vistos: Counter[str] = Counter()
    for q in QUESTIONS:
        stem = q["stem"]
        vistos[stem] += 1
        alts = q["alternatives"]
        correctas = [a for a in alts if a["is_correct"]]

        if q["skill_node"] not in CODIGOS:
            fallas.append(f"nodo inexistente '{q['skill_node']}': {stem[:60]}")
        if q["difficulty"] not in DIFICULTADES:
            fallas.append(f"dificultad inválida '{q['difficulty']}': {stem[:60]}")
        if len(alts) != 4:
            fallas.append(f"tiene {len(alts)} alternativas, deben ser 4: {stem[:60]}")
        if len(correctas) != 1:
            fallas.append(f"tiene {len(correctas)} correctas, debe ser 1: {stem[:60]}")
        if not q["explanation"].strip():
            fallas.append(f"sin explicación: {stem[:60]}")

        textos = [a["text"] for a in alts]
        if len(set(textos)) != len(textos):
            fallas.append(f"alternativas repetidas: {stem[:60]}")
        for a in alts:
            if not a["is_correct"] and not a["justification"]:
                fallas.append(f"distractor sin justificación: {stem[:60]}")

        # seed.py mezcla el orden: nada puede referirse a "la alternativa A".
        textos_libres = [q["explanation"]] + [a["justification"] or "" for a in alts]
        for t in textos_libres:
            if re.search(r"\balternativa [A-D]\b|\bopción [A-D]\b", t):
                fallas.append(f"menciona una letra de alternativa: {stem[:60]}")

    # Dos preguntas del mismo nodo con los mismos números suelen ser la misma
    # pregunta con otra redacción: al estudiante le tocan repetidas en un ensayo.
    por_firma: dict[tuple[str, tuple[str, ...]], list[str]] = {}
    for q in QUESTIONS:
        numeros = tuple(sorted(re.findall(r"\d+(?:[.,]\d+)?", q["stem"])))
        if not numeros:
            continue
        por_firma.setdefault((q["skill_node"], numeros), []).append(q["stem"])
    for (nodo, numeros), stems in por_firma.items():
        if len(stems) > 1:
            print(f"  aviso: {nodo} tiene {len(stems)} preguntas con los números {numeros}")
            for st in stems:
                print(f"      {st[:78]}")

    for stem, veces in vistos.items():
        if veces > 1:
            fallas.append(f"enunciado duplicado {veces} veces: {stem[:70]}")

    # ---- capa 2: aritmética ----
    por_stem = {q["stem"]: q for q in QUESTIONS}
    comprobadas = 0
    for fragmento, esperado in COMPROBACIONES.items():
        candidatas = [s for s in por_stem if fragmento in s]
        if len(candidatas) != 1:
            fallas.append(
                f"el fragmento '{fragmento}' calza con {len(candidatas)} enunciados"
            )
            continue
        q = por_stem[candidatas[0]]
        correcta = next(a["text"] for a in q["alternatives"] if a["is_correct"])
        if _norm(esperado) not in _norm(correcta):
            fallas.append(
                f"aritmética: '{fragmento}' → esperado '{esperado}', "
                f"la marcada correcta dice '{correcta}'"
            )
        comprobadas += 1

    # ---- reporte ----
    print(f"preguntas en el banco: {len(QUESTIONS)}")
    print(f"comprobaciones aritméticas ejecutadas: {comprobadas}")
    por_nodo = Counter(q["skill_node"] for q in QUESTIONS)
    sin_suficientes = [c for c in CODIGOS if por_nodo[c] < 5]
    if sin_suficientes:
        print(f"nodos con menos de 5 preguntas: {sorted(sin_suficientes)}")

    if fallas:
        print(f"\n{len(fallas)} PROBLEMAS:")
        for f in fallas:
            print(f"  - {f}")
        return 1
    print("\nsin problemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
