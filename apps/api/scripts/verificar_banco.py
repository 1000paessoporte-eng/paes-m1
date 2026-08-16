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

from paes_api.seed_data import (
    LESSONS,
    PASSAGES,
    PASSAGES_HISTORIA,
    QUESTIONS,
    QUESTIONS_CIENCIAS,
    QUESTIONS_HISTORIA,
    QUESTIONS_LECTORA,
    SKILL_NODES,
    SKILL_NODES_CIENCIAS,
    SKILL_NODES_HISTORIA,
    SKILL_NODES_LECTORA,
    SKILL_NODES_M2,
)

CODIGOS = (
    {n[0] for n in SKILL_NODES}
    | {n[0] for n in SKILL_NODES_M2}
    | {n[0] for n in SKILL_NODES_LECTORA}
    | {n[0] for n in SKILL_NODES_CIENCIAS}
    | {n[0] for n in SKILL_NODES_HISTORIA}
)
TODOS_LOS_PASAJES = PASSAGES + PASSAGES_HISTORIA
CLAVES_PASAJE = {p["key"] for p in TODOS_LOS_PASAJES}
PASAJES_POR_CLAVE = {p["key"]: p for p in TODOS_LOS_PASAJES}
DIFICULTADES = {"facil", "medio", "dificil"}

# Resultado final del ejemplo resuelto de cada lección, recalculado acá sin
# mirar el texto. Una lección con la aritmética mala es peor que no tener
# lección: el estudiante la estudia creyendo que está bien.
#
# ALCANCE: comprueba que el resultado correcto aparezca en la resolución, no
# que cada paso intermedio esté bien — para eso haría falta un motor simbólico.
# Si alguien cambia un número intermedio y el final sigue apareciendo en otro
# paso, esto no lo detecta. Detecta lo que importa más: que el ejemplo termine
# donde debe terminar.
RESULTADOS_LECCIONES: dict[str, Fraction] = {
    "num_racionales": Fraction(5, 6) - Fraction(2, 9),                # 11/18
    "num_potencias_raices": Fraction(2**5) * Fraction(1, 2**3) * 2,   # 8
    "num_porcentajes": Fraction(round(20000 * 1.20 * 0.85)),          # 20.400
    "alg_lineal": Fraction(9),                                        # x = 9
    "alg_sistemas": Fraction(7),                                      # x = 7
    "alg_cuadratica": Fraction(3),                                    # x = 2 o 3
    "alg_funciones": Fraction(3),                                     # pendiente 3
    "geo_plana": Fraction(round((8 * 5 - 3.14 * 2**2) * 100), 100),   # 27,44
    "geo_pitagoras": Fraction(int(sqrt(13**2 - 5**2))),               # 12
    "geo_transformaciones": Fraction(5),                              # (5, 3)
    "geo_solidos": Fraction(round(3.14 * 10**2 * 20)),                # 6.280
    "prob_estadistica_desc": Fraction(4 + 5 + 5 + 6 + 10, 5),         # 6
    "prob_combinatoria": Fraction(comb(6, 2)),                        # 15
    "prob_reglas": Fraction(5, 8) * Fraction(4, 7),                   # 5/14
}

# --- Ciencias: física y química ---
# Cada valor se recalcula acá desde la definición, sin mirar la alternativa que
# el banco marcó como correcta. Es la única forma de que un error de cálculo no
# pase silenciosamente a un estudiante que lo va a estudiar como verdad.
COMPROBACIONES_CIENCIAS: dict[str, str] = {
    # Movimiento
    "Un tren viaja a 90 km/h": str(round(90 / 3.6)),
    "se deja caer desde el reposo": str(10 * 3),
    "aumenta su rapidez de 5 m/s a 25 m/s": str((25 - 5) // 4),
    "rapidez constante de 25 m/s durante 8": str(25 * 8),
    "frena uniformemente hasta detenerse en 5": str((0 - 20) // 5),
    # Fuerzas
    "peso de un cuerpo de 8 kg": str(8 * 10),
    "una de 30 N hacia la derecha": str((30 - 12) // 6),
    "empujada con una fuerza de 40 N": str((40 - 10) // 5),
    "dos fuerzas perpendiculares": str(int(sqrt(3**2 + 4**2))),
    # Energía
    "energía potencial gravitatoria de un cuerpo de 2 kg": str(2 * 10 * 5),
    "cuerpo de 4 kg se mueve a 3 m/s": str(int(0.5 * 4 * 3**2)),
    "trabajo de 600 J en 20 segundos": str(600 // 20),
    "se suelta desde 20 m de altura": str(int(sqrt(2 * 10 * 20))),
    "fuerza de 25 N desplaza un cuerpo 8 m": str(25 * 8),
    # Ondas
    "periodo de 0,2 s": str(int(1 / 0.2)),
    "frecuencia de 170 Hz": str(340 // 170),
    "longitud de onda de 3 m y una frecuencia de 12": str(3 * 12),
    # Electricidad
    "ampolleta conectada a 220 V": str(int(220 / 0.5)),
    "4 Ω y 6 Ω se conectan en SERIE": str(4 + 6),
    "funciona con 12 V y consume 2 A": str(12 * 2),
    "resistencia de 10 Ω es atravesada por una corriente de 3 A": str(3**2 * 10),
    # Átomo
    "átomo neutro tiene 11 protones": str(11),
    "ion $Ca^{2+}$": str(20 - 2),
    "número másico 40 y 20 neutrones": str(40 - 20),
    # Estequiometría y disoluciones
    "17 protones y 18 neutrones": str(17 + 18),
    "preparar 2 litros de una disolución 0,5 mol/L? La masa molar": str(int(0.5 * 2 * 40)),
    "3 moles de agua": str(3 * 18),
    "4 moles de nitrógeno": str(4 * 2),
    "2 moles de soluto en 4 litros": str(2 / 4),
    "500 mL de una disolución 0,4": str(0.4 * 0.5),
    "diluye una disolución de 100 mL y 2 mol/L": str(2 * 100 / 400),
    # Competencia Lectora: la tabla de residuos
    "aumentaron los plásticos": str(22 - 12),
    # Competencia Lectora: la campaña del agua
    "aplica las dos primeras medidas": str(30 + 15),
    "gasta 150 litros al día": str(150 * 4),
    # Historia y Cs. Sociales: economía y cálculo temporal
    "4.500.000 personas ocupadas": str(round(500_000 / (4_500_000 + 500_000) * 100)),
    "IPC de un país pasa de 100 a 106": str(round((106 - 100) / 100 * 100)),
    "PIB de 300.000 millones": f"{300_000 // 20:,}".replace(",", "."),
    "fuerza de trabajo es de 60.000": str(round(3_000 / 60_000 * 100)),
    "ofrecen 800 unidades": str(800 - 500),
    "vende 200 unidades a 3.000 pesos": f"{3_000 * 200:,}".replace(",", "."),
    "cayó el sector primario": str(55 - 11),
    "comienza en 1810 y termina en 1830": str(1830 - 1810),
    # Segunda tanda de Ciencias
    "recorre 300 m en 20 s": str((300 + 100) // (20 + 5)),
    "lanza verticalmente hacia arriba a 30 m/s": str(30 // 10),
    "viaja a 15 m/s y acelera a 3": str(int(15 * 6 + 0.5 * 3 * 6**2)),
    "ascensor sube con aceleración": str(60 * (10 + 2)),
    "coeficiente de roce 0,3": str(int(0.3 * 10 * 10)),
    "cuerpo de 2 kg cuelga en reposo": str(2 * 10),
    "cuerpo de 2 kg cae desde 10 m": str(2 * 10 * 10),
    "ampolleta de 60 W permanece encendida": str(60 / 1000 * 5).replace(".", ","),
    "recibe 500 J y entrega 350 J": str(round(350 / 500 * 100)),
    "frecuencia de 25 Hz. ¿Cuántas": str(25 * 4),
    "artefacto de 1.100 W": str(1100 // 220),
    "Tres resistencias de 6 Ω cada una": str(6 // 3),
    "40 g de hidróxido de sodio (NaOH)": str(40 // 40),
    "6 moles de óxido de magnesio": str(6),
    "20 g de sal en 180 g de agua": str(round(20 / (20 + 180) * 100)),
    "pH 3 y otra pH 5": str(10 ** (5 - 3)),
    # Tercera tanda de Ciencias
    "atleta corre 400 m en 50 s": str(400 // 50),
    "recorre 240 m en 12 s": str(240 // 12 * 20),
    "cae libremente desde el reposo durante 4 s": str(int(0.5 * 10 * 4**2)),
    "auto a 30 m/s frena": str(30 // 5),
    "alcanza 12 m/s en 4 s": str(12 // 4),
    "tren de 200 m viaja a 20 m/s": str((600 + 200) // 20),
    "parten del mismo punto en sentidos opuestos": str((15 + 25) * 10),
    "cuerpo de 12 kg acelere a 3": str(12 * 3),
    "20 kg sube por una cuerda": str(20 * (10 + 3)),
    "fuerza de 50 N hacia la derecha": str((50 - 20) // 5),
    "cuerpo de 6 kg está en reposo sobre una mesa": str(6 * 10),
    "de 3 kg y 5 kg, son arrastrados": str(24 // (3 + 5)),
    "cuerpo de 10 kg se mueve a 6 m/s": str(int(0.5 * 10 * 6**2)),
    "bomba eleva 200 kg de agua": str(200 * 10 * 5 // 20),
    "carrito de 2 kg baja sin roce": str(int((2 * 10 * 5) ** 0.5)),
    "motor consume 2.000 J": str(2000 - 1200),
    "grúa levanta 300 kg a 6 m": f"{300 * 10 * 6:,}".replace(",", "."),
    "longitud de onda de 2 m y avanza a 10 m/s": str(10 // 2),
    "onda sonora de 680 Hz": str(340 / 680).replace(".", ","),
    "periodo de 0,05 s": str(int(1 / 0.05)),
    "resistencia de 25 Ω se conecta a una fuente de 100 V": str(100 // 25),
    "estufa de 2.000 W funciona 3 horas": str(2000 // 1000 * 3),
    "10 Ω y 15 Ω se conectan en serie": str(100 // (10 + 15)),
    "aparato de 60 W conectado a 120 V": str(120**2 // 60),
    "ion tiene 16 protones y 18 electrones": str(18 - 16),
    "2 moles de oxígeno molecular": str(2 * 32),
    "quemar 4 moles de carbono": str(4),
    "36 g de agua, si su masa molar es 18": str(36 // 18),
    "partir de 4 moles de hidrógeno": str(4 * 18),
    "oxígeno hay en total en $3H_2SO_4$": str(3 * 4),
    "3 moles de soluto en 1,5 litros": str(int(3 / 1.5)),
    "200 mL de una disolución 3 mol/L": str(3 * 200 // 600),
    "250 mL de una disolución 0,4 mol/L de": str(int(0.4 * 0.25 * 60)),
    "40 g de soluto en 160 g de agua": str(round(40 / (40 + 160) * 100)),
    "2 litros de disolución 0,5 mol/L. ¿Cuántos moles": str(int(0.5 * 2)),
    "10^{-9}$ mol/L": str(9),
    "pOH 4, ¿cuál es su pH": str(14 - 4),
    "pH 2 y otra pH 6": f"{10 ** (6 - 2):,}".replace(",", "."),
    # Segunda tanda de Historia: economía
    "IPC sube de 120 a 126": str(round((126 - 120) / 120 * 100)),
    "PIB de 120.000 millones y 8 millones": f"{120_000 // 8:,}".replace(",", "."),
    "8 millones de personas en edad de trabajar": str(round(500 / 5500 * 100, 1)).replace(".", ","),
    "a $500 los consumidores demandan 900": str(900 - 400),
    "vende 500 unidades a $2.000": f"{2_000 * 500 - 700_000:,}".replace(",", "."),
    "sector terciario entre 1960 y 2000": str(52 - 25),
    "aumentaron los plásticos entre 2015": str(22 - 12),
    # Fuentes nuevas de Historia
    "mujeres rurales entre 1930 y 2020": str(96 - 19),
    "plebiscito de 2020 que en la municipal de 2016": f"{23_000 - 15_400:,}".replace(",", "."),
    # Biología: lo que sí se puede recalcular
    "saca 3 iones": str(3 - 2),
    "se divide por mitosis": str(46),
    "moléculas de $CO_2$ se necesitan": str(6),
    "dos plantas heterocigotas": str(round(1 / 4 * 100)),
    "heterocigota $Aa$ con una homocigota recesiva": str(round(1 / 2 * 100)),
    "entra en meiosis": str(46 // 2),
    "porcentaje de los HIJOS VARONES": str(round(1 / 2 * 100)),
    "grupo sanguíneo $AB$": str(round(2 / 4 * 100)),
    "los productores fijan 10.000 kcal": str(int(10_000 * 0.1 * 0.1)),
    "consumidor primario recibe 500 kcal": f"{int(500 / 0.1):,}".replace(",", "."),
    "8.000 kcal en los productores": str(int(8_000 * 0.1 * 0.1 * 0.1)),
    # Ácido-base
    "concentración de iones hidrógeno es $1 \\times 10^{-5}$": str(5),
}

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
    # --- reglas de las probabilidades: segunda tanda ---
    # Cada valor se recalcula acá desde los datos del enunciado, sin mirar la
    # alternativa marcada como correcta. Si alguien edita una pregunta y le
    # descuadra la aritmética, esto lo caza.
    "ruleta tiene 20 sectores iguales": str(Fraction(4, 20)),
    "32 estudiantes, de los cuales 18 son mujeres": str(Fraction(32 - 18, 32)),
    "9 caramelos de limón y 15 de frutilla": str(Fraction(9, 9 + 15)),
    "el bus llegue atrasado a cierto paradero es 0,15": str(round(1 - 0.15, 2)).replace(".", ","),
    "dado de 12 caras numeradas del 1 al 12": str(Fraction(3, 12)),
    "naipe español tiene 40 cartas": str(Fraction(40 // 4, 40)),
    "25 autos y 10 de ellos son rojos": str(Fraction(25 - 10, 25)),
    # Excluyentes: se suman sin descontar nada.
    "compre solamente bebida es 0,35": str(round(0.35 + 0.45, 2)).replace(".", ","),
    # Con intersección: la regla aditiva descuenta los contados dos veces.
    "22 juegan fútbol, 16 juegan vóleibol": str(Fraction(22 + 16 - 8, 40)),
    "máquina A esté operativa en un día cualquiera": str(round(0.9 * 0.8, 2)).replace(".", ","),
    # Sin reposición: la segunda extracción cambia numerador y denominador.
    "5 lápices azules y 3 rojos": str(Fraction(3, 8) * Fraction(2, 7)),
    "arquero acierta al blanco con probabilidad 0,6": str(round(0.6 * 0.6, 2)).replace(".", ","),
    "lanzan tres monedas equilibradas": str(1 - Fraction(1, 2) ** 3),
    "120 prefieren té, 50 prefieren café": str(Fraction(120 + 50, 200)),
    "180 usan transporte público": str(Fraction(180 + 140 - 90, 300)),
    # Distinto color: los dos órdenes posibles, sumados.
    "7 fichas verdes y 5 moradas": str(2 * Fraction(7, 12) * Fraction(5, 11)),
    "cada uno falla con probabilidad 0,1": str(round(1 - 0.9**3, 3)).replace(".", ","),
    "ganar el premio principal es 0,45": str(round(1 - (0.45 + 0.3 - 0.15), 2)).replace(".", ","),
    "De 10 postulantes a un cargo": str(1 - Fraction(6, 10) * Fraction(5, 9)),
    # Ponderar por producción antes de sumar: 60% y 40% no pesan igual.
    "máquina A produce el 60% de las piezas": str(round(0.6 * 0.05 + 0.4 * 0.02, 3)).replace(".", ","),
    # --- Historia: economía y lectura de tabla ---
    "8.000.000 de personas en la fuerza de trabajo": f"{640000 / 8000000 * 100:.0f}%",
    "canasta de bienes costaba $50.000": f"{(53500 - 50000) / 50000 * 100:.0f}%",
    "aumentó la población total de la comuna": f"{28700 - 12400:,}".replace(",", ".") + " habitantes",
    # --- Ciencias: física ---
    "recorre 120 m en 15 s": f"{120 // 15} m/s",
    "acelera uniformemente a 2 m/s² durante 6 s": f"{0.5 * 2 * 6**2:.0f} m",
    "cuerpo de 4 kg actúa una fuerza neta de 20 N": f"{20 // 4} m/s²",
    "caja de 50 kg a 4 m de altura": f"{50 * 10 * 4} J",
    "frecuencia de 50 Hz y una longitud de onda de 4 m": f"{50 * 4} m/s",
    "resistencia de 20 Ω circula una corriente de 3 A": f"{3 * 20} V",
    "6 Ω y 3 Ω se conectan en paralelo": f"{1 / (1/6 + 1/3):.0f} Ω",
    # --- Ciencias: química ---
    "número atómico 17 y número másico 35": str(35 - 17),
    "88 g de dióxido de carbono": f"{88 // 44} mol",
    "0,5 mol de soluto": f"{0.5 / 0.25:.0f} mol/L",
    "1 × 10⁻³ mol/L": str(3),
    "pH de una disolución es 5": str(14 - 5),
    "6 mol de hidrógeno": "6 mol",
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
    # --- ecuaciones cuadráticas ---
    "x² − 36 = 0": f"x = {int(sqrt(36))} y x = −{int(sqrt(36))}",
    "x² = 81": f"x = {int(sqrt(81))} y x = −{int(sqrt(81))}",
    "x² − 6x = 0": f"x = 0 y x = {6}",
    "x² + 5x + 6 = 0": f"x = −{2} y x = −{3}" if 2 * 3 == 6 and 2 + 3 == 5 else "?",
    "x² − 9x + 20 = 0": f"x = {4} y x = {5}" if 4 * 5 == 20 and 4 + 5 == 9 else "?",
    "x² + 3x − 18 = 0": f"x = {3} y x = −{6}" if 3 * -6 == -18 and 3 - 6 == -3 else "?",
    "x² − 2x − 8 = 0": f"x = {4} y x = −{2}" if 4 * -2 == -8 and 4 - 2 == 2 else "?",
    "3x² − 12 = 0": f"x = {int(sqrt(12 // 3))} y x = −{int(sqrt(12 // 3))}",
    "x² − 10x + 25 = 0": f"x = {10 // 2}",
    "2x² − 5x − 3 = 0": f"x = {3} y x = −1/2" if 2 * 3**2 - 5 * 3 - 3 == 0 else "?",
    "largo mide 3 cm más que su ancho": f"{5} cm" if 5 * (5 + 3) == 40 else "?",
    "menos el triple de ese mismo número": str(7) if 7**2 - 3 * 7 == 28 else "?",
    "x² − 4x − 12 = 0": f"x = {6} y x = −{2}" if 6 * -2 == -12 and 6 - 2 == 4 else "?",
    "2x² + 7x + 3 = 0": f"x = −{3} y x = −1/2" if 2 * 3**2 - 7 * 3 + 3 == 0 else "?",
    "x² − 6x + 9 = 0": str((-6) ** 2 - 4 * 1 * 9),
    "2x² + 3x + 5 = 0": str(3**2 - 4 * 2 * 5),
    "h = −5t² + 20t": f"{20 // 5} segundos",
    "soluciones de una ecuación cuadrática son x = 3 y x = −4": "(x − 3)(x + 4) = 0",
    "suma de las soluciones de la ecuación x² − 7x + 10 = 0": str(2 + 5) if 2 * 5 == 10 and 2 + 5 == 7 else "?",
    "producto de dos números enteros consecutivos es 72": str(8) if 8 * 9 == 72 else "?",
    "x² − 121 = 0": f"x = {int(sqrt(121))} y x = −{int(sqrt(121))}",
    "x² = 144": f"x = {int(sqrt(144))} y x = −{int(sqrt(144))}",
    "x² + 8x = 0": f"x = 0 y x = −{8}",
    "x² + 6x + 8 = 0": f"x = −{2} y x = −{4}" if 2 * 4 == 8 and 2 + 4 == 6 else "?",
    "x² − 11x + 24 = 0": f"x = {3} y x = {8}" if 3 * 8 == 24 and 3 + 8 == 11 else "?",
    "x² − x − 20 = 0": f"x = {5} y x = −{4}" if 5 * -4 == -20 and 5 - 4 == 1 else "?",
    "x² + 4x − 21 = 0": f"x = {3} y x = −{7}" if 3 * -7 == -21 and 3 - 7 == -4 else "?",
    "5x² − 45 = 0": f"x = {int(sqrt(45 // 5))} y x = −{int(sqrt(45 // 5))}",
    "x² + 12x + 36 = 0": f"x = −{12 // 2}",
    "3x² − 10x + 3 = 0": f"x = {3} y x = 1/3" if 3 * 3**2 - 10 * 3 + 3 == 0 else "?",
    "5 m más de largo que de ancho": f"{7} m" if 7 * (7 + 5) == 84 else "?",
    "suma de un número y su cuadrado": str(6) if 6 + 6**2 == 42 else "?",
    "fórmula general, ¿cuáles son las soluciones de x² − 3x − 10 = 0": (
        f"x = {5} y x = −{2}" if 5 * -2 == -10 and 5 - 2 == 3 else "?"
    ),
    "3x² + 5x − 2 = 0": (
        f"x = 1/3 y x = −{2}"
        if 3 * Fraction(1, 3) ** 2 + 5 * Fraction(1, 3) - 2 == 0
        else "?"
    ),
    "x² + 4x + 4 = 0": str(4**2 - 4 * 1 * 4),
    "x² − 2x + 7 = 0": str((-2) ** 2 - 4 * 1 * 7),
    "h = −5t² + 30t": f"{30 // 5} segundos",
    "soluciones de una ecuación cuadrática son x = −2 y x = 5": "(x + 2)(x − 5) = 0",
    "producto de las soluciones de la ecuación x² − 9x + 18 = 0": (
        str(3 * 6) if 3 * 6 == 18 and 3 + 6 == 9 else "?"
    ),
    "cuadrado de la edad de Ana": f"{9} años" if 9**2 - 4 * 9 == 45 else "?",
    # --- funciones lineales y cuadráticas ---
    "f(x) = 4x + 1": str(4 * 3 + 1),
    "f(x) = x² − 2": str(4**2 - 2),
    "(2, 3) y (6, 11)": str((11 - 3) // (6 - 2)),
    "pendiente de la recta y = 5x − 2": str(5),
    "corta al eje Y la recta y = 3x + 7": f"(0, {7})",
    "vértice de la parábola y = x² − 8x + 12": f"({8 // 2}, {(8 // 2) ** 2 - 8 * (8 // 2) + 12})",
    "eje de simetría de la parábola y = x² + 4x − 5": f"x = {-4 // 2}",
    "eje X de la parábola y = x² − 5x + 6": "(2, 0) y (3, 0)" if 2 * 3 == 6 and 2 + 3 == 5 else "?",
    "(0, 5) y tiene pendiente −2": f"y = −2x + {5}",
    "f(x) = 3x + b cumple que f(2) = 11": str(11 - 3 * 2),
    "función que representa el costo total": f"C(x) = {300}x + {500}",
    "viaje de 8 kilómetros": f"${300 * 8 + 500:,}".replace(",", "."),
    "f(x) = −2x + 7 cuando x = −3": str(-2 * -3 + 7),
    "vértice de la parábola y = 2x² − 8x + 5": f"({8 // (2 * 2)}, {2 * 2**2 - 8 * 2 + 5})",
    "valor mínimo que alcanza la función y = x² − 6x + 11": str(3**2 - 6 * 3 + 11),
    "(1, 4) y (3, 10)": f"y = {(10 - 4) // (3 - 1)}x + {4 - ((10 - 4) // (3 - 1))}",
    "f(x) = 4x − 20 se hace cero": f"x = {20 // 4}",
    "I(x) = 50x": f"{900 // (50 - 20)} unidades",
    "(−2, 1) y (2, 9)": str((9 - 1) // (2 - (-2))),
    "y = x² + bx + 3 pasa por el punto (1, 6)": str(6 - 1 - 3),
    "f(x) = 2x − 5": str(2 * 4 - 5),
    "f(x) = x² + 3": str(2**2 + 3),
    "(0, 0) y (4, 12)": str(12 // 4),
    "pendiente de la recta y = −3x + 8": str(-3),
    "corta al eje Y la recta y = −4x + 2": f"(0, {2})",
    "f(x) = 6 − x": str(6 - 10),
    "vértice de la parábola y = x² + 2x − 3": f"({-2 // 2}, {(-1) ** 2 + 2 * (-1) - 3})",
    "eje de simetría de la parábola y = 2x² − 12x + 7": f"x = {12 // (2 * 2)}",
    "eje X de la parábola y = x² − 9": f"({int(sqrt(9))}, 0) y (−{int(sqrt(9))}, 0)",
    "(2, 7) y tiene pendiente 3": f"y = 3x + {7 - 3 * 2}",
    "f(x) = mx + 2 cumple que f(4) = 14": str((14 - 2) // 4),
    "$200 por cada GB adicional": f"${12000 + 200 * 15:,}".replace(",", "."),
    "V(t) = 2000 − 50t": f"{2000 - 50 * 12:,}".replace(",", "."),
    "vértice de la parábola y = −x² + 4x + 1": f"({-4 // (2 * -1)}, {-(2**2) + 4 * 2 + 1})",
    "valor máximo que alcanza la función y = −2x² + 8x − 3": str(-2 * 2**2 + 8 * 2 - 3),
    "(−1, 2) y (2, 11)": f"y = {(11 - 2) // 3}x + {2 - ((11 - 2) // 3) * (-1)}",
    "corta al eje X la recta y = 5x − 15": f"({15 // 5}, 0)",
    "I(x) = 40x": f"{1000 // (40 - 15)} unidades",
    "(3, −2) y (7, 6)": str((6 - (-2)) // (7 - 3)),
    "y = ax² + 2 pasa por el punto (2, 14)": str((14 - 2) // 2**2),
    "f(x) = x² − 4x": str((-1) ** 2 - 4 * (-1)),
    # ================= LOTE 6 — eje NÚMEROS =================
    "1/3 + 2/5": str(Fraction(1, 3) + Fraction(2, 5)),
    "7/10 − 2/5": str(Fraction(7, 10) - Fraction(2, 5)),
    "3/8 × 4/9": str(Fraction(3, 8) * Fraction(4, 9)),
    "(5/6) ÷ (5/12)": str(Fraction(5, 6) / Fraction(5, 12)),
    "2/3 + 1/6 + 1/2": str(Fraction(2, 3) + Fraction(1, 6) + Fraction(1, 2)),
    "3/4 de taza de azúcar": str(Fraction(3, 4) * Fraction(1, 2)),
    "1 − (2/7 + 1/3)": str(1 - (Fraction(2, 7) + Fraction(1, 3))),
    "(3/4) × (8/15)": str(Fraction(3, 4) * Fraction(8, 15)),
    "5/2 ÷ 3/4": str(Fraction(5, 2) / Fraction(3, 4)),
    "estanque está lleno hasta 5/6": str(Fraction(5, 6) - Fraction(2, 5) * Fraction(5, 6)),
    "3 − 2/5 × 5/6": str(3 - Fraction(2, 5) * Fraction(5, 6)),
    "albañil avanza 3/8": str(Fraction(3, 8) + Fraction(1, 4)),
    "(1/2 + 1/3) ÷ (1/2 − 1/3)": str(
        (Fraction(1, 2) + Fraction(1, 3)) / (Fraction(1, 2) - Fraction(1, 3))
    ),
    "m = 3/4 y n = 2/3": str(
        Fraction(3, 4) * Fraction(2, 3) + Fraction(3, 4) / Fraction(2, 3)
    ),
    "(2/3)² + 1/9": str(Fraction(2, 3) ** 2 + Fraction(1, 9)),
    "depósito está lleno hasta sus 3/5": str(1 - (Fraction(3, 5) + Fraction(2, 7))),
    "dos fracciones es mayor: 5/8 o 7/12": (
        "5/8" if Fraction(5, 8) > Fraction(7, 12) else "7/12"
    ),
    "Ordena de menor a mayor las fracciones": ", ".join(
        str(f) for f in sorted([Fraction(2, 3), Fraction(3, 5), Fraction(7, 10)])
    ),
    "(3/4 − 1/6) ÷ (1/2 + 1/3)": str(
        (Fraction(3, 4) - Fraction(1, 6)) / (Fraction(1, 2) + Fraction(1, 3))
    ),
    "3/4 de kilo de café en 6 bolsas": str(Fraction(3, 4) / 6),
    "el valor de 4³": str(4**3),
    "√100 + √9": str(int(sqrt(100) + sqrt(9))),
    "2⁵ · 2²": str(2**5 * 2**2),
    "(2²)⁴": str((2**2) ** 4),
    "10⁻²": str(Fraction(1, 10**2)),
    "√64 · √4": str(int(sqrt(64) * sqrt(4))),
    "(4³ · 4²) ÷ 4⁴": str(4**3 * 4**2 // 4**4),
    "√72 en su forma más simple": "6" if isclose(sqrt(72), 6 * sqrt(2)) else "?",
    "(5²)³ ÷ 5⁴": str((5**2) ** 3 // 5**4),
    "3⁰ + 2⁻¹": str(1 + Fraction(1, 2)),
    "√98 − √50": "2" if isclose(sqrt(98) - sqrt(50), 2 * sqrt(2)) else "?",
    "plaza cuadrada tiene un área de 121 m²": f"{int(sqrt(121))} m",
    "2⁻³ · 2⁵": str(2 ** (-3 + 5)),
    "5ˣ = 625": str(4 if 5**4 == 625 else None),
    "(3⁻² · 3⁵) ÷ 3²": str(3 ** (-2 + 5 - 2)),
    "√(5² + 12²)": str(int(sqrt(5**2 + 12**2))),
    "2³ + 3²": str(2**3 + 3**2),
    "√(16 · 25)": str(int(sqrt(16 * 25))),
    "(7²)⁰": str(7**0),
    "2^(x−1) = 16": str(5 if 2 ** (5 - 1) == 16 else None),
    # --- porcentajes y proporcionalidad ---
    "25% de 320": str(round(0.25 * 320)),
    "60% de 45": str(round(0.6 * 45)),
    "$16.000 y tiene un descuento del 10%": f"${round(16000 * 0.9):,}".replace(",", "."),
    "sueldo de $450.000 sube un 8%": f"${round(450000 * 1.08):,}".replace(",", "."),
    "representa 18 de un total de 60": f"{round(18 / 60 * 100)}%",
    "representa 9 de un total de 36": f"{round(9 / 36 * 100)}%",
    "descuento del 40%, un producto queda en $9.000": f"${round(9000 / 0.6):,}".replace(",", "."),
    "subió de $8.000 a $10.000": f"{round((10000 - 8000) / 8000 * 100)}%",
    "bajó de $25.000 a $20.000": f"{round((25000 - 20000) / 25000 * 100)}%",
    "votaron 4.500 personas": f"{round(4500 * 0.36):,}".replace(",", "."),
    "El 15% de un número es 45": str(round(45 / 0.15)),
    "curso de 30 estudiantes, el 40% son hombres": str(round(30 * 0.6)),
    "descuentos sucesivos de 10% y 20%": f"${round(60000 * 0.9 * 0.8):,}".replace(",", "."),
    "sube un 30% y luego baja un 30%": f"{round((1 - 1.3 * 0.7) * 100)}%",
    "Cinco máquinas producen 200 piezas": f"{200 * 8 // 5} piezas",
    "Tres obreros pintan una casa en 12 días": f"{3 * 12 // 4} días",
    "aumenta un 20% y después ese nuevo monto aumenta un 25%": f"{round((1.2 * 1.25 - 1) * 100)}%",
    "camisa cuesta $19.900": f"${round(19900 * 0.7):,}".replace(",", "."),
    "IVA incluido de 19% es $23.800": f"${round(23800 / 1.19):,}".replace(",", "."),
    "120% de 250": str(round(1.2 * 250)),
    # ================= LOTE 7 — eje GEOMETRÍA =================
    "área de un cuadrado de lado 7 cm": f"{7**2} cm²",
    "perímetro de un cuadrado de lado 9 cm": f"{4 * 9} cm",
    "rectángulo de 12 cm de largo y 6 cm de ancho": f"{12 * 6} cm²",
    "perímetro de un rectángulo de 15 cm de largo y 8 cm": f"{2 * (15 + 8)} cm",
    "triángulo de base 14 cm y altura 5 cm": f"{14 * 5 // 2} cm²",
    "triángulo equilátero de lado 12 cm": f"{3 * 12} cm",
    "círculo de radio 4 cm": f"{3.14 * 4**2:.2f} cm²".replace(".", ","),
    "circunferencia de radio 7 cm": f"{2 * 3.14 * 7:.2f} cm".replace(".", ","),
    "bases de 10 cm y 6 cm, y una altura de 4 cm": f"{(10 + 6) * 4 // 2} cm²",
    "diagonales que miden 12 cm y 8 cm": f"{12 * 8 // 2} cm²",
    "cancha rectangular mide 30 m de largo y 18 m": f"{2 * (30 + 18)} m",
    "sala rectangular mide 6,5 m por 4 m": f"{round(6.5 * 4)} m²",
    "cuadrado tiene un perímetro de 48 cm": f"{(48 // 4) ** 2} cm²",
    "área de 36 cm² y su altura mide 9 cm": f"{2 * 36 // 9} cm",
    "círculo tiene un diámetro de 10 cm": f"{3.14 * (10 / 2) ** 2:.1f} cm²".replace(".", ","),
    "perímetro de 44 m y su largo mide 4 m más": f"{9 * (9 + 4)} m²",
    "radio de un círculo se duplica": str(2**2),
    "cuadrado de lado 8 cm tiene inscrito": f"{8**2 - 3.14 * 4**2:.2f} cm²".replace(".", ","),
    "paralelogramo de base 9 cm y altura 5 cm": f"{9 * 5} cm²",
    "piscina rectangular mide 12 m por 5 m": f"{(12 + 2) * (5 + 2) - 12 * 5} m²",
    # --- teorema de Pitágoras ---
    "catetos de 5 cm y 12 cm": f"{int(sqrt(5**2 + 12**2))} cm",
    "catetos de 8 cm y 15 cm": f"{int(sqrt(8**2 + 15**2))} cm",
    "hipotenusa mide 10 cm y uno de sus catetos mide 6 cm": f"{int(sqrt(10**2 - 6**2))} cm",
    "hipotenusa mide 17 cm y un cateto mide 8 cm": f"{int(sqrt(17**2 - 8**2))} cm",
    "catetos de 7 cm y 24 cm": f"{int(sqrt(7**2 + 24**2))} cm",
    "rectángulo que mide 9 cm por 12 cm": f"{int(sqrt(9**2 + 12**2))} cm",
    "diagonal de un cuadrado de lado 10 cm": "10" if isclose(sqrt(2 * 100), 10 * sqrt(2)) else "?",
    "rampa sube 3 m de altura": f"{int(sqrt(3**2 + 4**2))} m",
    "mástil de 12 m de alto": f"{int(sqrt(12**2 + 5**2))} m",
    "catetos de 20 cm y 21 cm": f"{int(sqrt(20**2 + 21**2))} cm",
    "hipotenusa mide 15 cm y un cateto mide 9 cm": f"{int(sqrt(15**2 - 9**2))} cm",
    "cancha rectangular mide 60 m por 80 m": f"{int(sqrt(60**2 + 80**2))} m",
    "SÍ puede formar un triángulo rectángulo": "9, 40 y 41" if 9**2 + 40**2 == 41**2 else "?",
    "hipotenusa 10 cm y un cateto de 6 cm": f"{6 * int(sqrt(10**2 - 6**2)) // 2} cm²",
    "escalera de 13 m se apoya": f"{int(sqrt(13**2 - 5**2))} m",
    "perímetro de un triángulo rectángulo de catetos 6 cm y 8 cm": (
        f"{6 + 8 + int(sqrt(6**2 + 8**2))} cm"
    ),
    "altura de un triángulo equilátero de lado 8 cm": (
        "4" if isclose(sqrt(8**2 - 4**2), 4 * sqrt(3)) else "?"
    ),
    "9 km hacia el norte": f"{int(sqrt(9**2 + 12**2))} km",
    "hipotenusa mide 26 cm y un cateto mide 10 cm": f"{int(sqrt(26**2 - 10**2))} cm",
    "diagonales que miden 16 cm y 12 cm": f"{int(sqrt(8**2 + 6**2))} cm",
    # --- transformaciones isométricas ---
    "(5, 2) se traslada según el vector (3, −4)": f"({5 + 3}, {2 - 4})",
    "(−1, 3) se traslada según el vector (2, 5)": f"({-1 + 2}, {3 + 5})",
    "(7, −2) al reflejarlo respecto del eje Y": f"({-7}, {-2})",
    "(−5, 4) al reflejarlo respecto del eje X": f"({-5}, {-4})",
    "(3, 0) se rota 90° en sentido antihorario": f"(0, {3})",
    "(0, 5) se rota 180°": f"(0, {-5})",
    "(2, 5) se rota 180°": f"({-2}, {-5})",
    "(4, 6) al reflejarlo respecto del origen": f"({-4}, {-6})",
    "(8, −3) se traslada según el vector (−5, 7)": f"({8 - 5}, {-3 + 7})",
    "(1, 4) se rota 90° en sentido antihorario": f"({-4}, {1})",
    "(−2, 3) se rota 90° en sentido horario": f"({3}, {2})",
    "A(2, 3) se refleja respecto del eje X": f"({2 + 1}, {-3 + 5})",
    "vector traslada el punto (2, 1) hasta el punto (7, −3)": f"({7 - 2}, {-3 - 1})",
    "(3, −5) se refleja respecto del eje Y y después se rota 180°": f"({3}, {5})",
    "vértices (0, 0), (4, 0) y (0, 3)": f"({4 + 2}, {0 + 5})",
    "lleva el punto (5, 2) al punto (2, 5)": "recta y = x",
    "(4, 1) se rota 270° en sentido antihorario": f"({1}, {-4})",
    "(−3, −2) se traslada según el vector (0, 6)": f"({-3}, {-2 + 6})",
    "(6, 8) se refleja respecto del origen": f"({-6 + 2}, {-8 - 3})",
    # --- cuerpos geométricos ---
    "volumen de un cubo de arista 3 cm": f"{3**3} cm³",
    "caja mide 6 cm de largo, 4 cm de ancho y 2 cm de alto": f"{6 * 4 * 2} cm³",
    "caras tiene un cubo": str(6),
    "vértices tiene un cubo": str(8),
    "área total de un cubo de arista 3 cm": f"{6 * 3**2} cm²",
    "cilindro de radio 5 cm y altura 4 cm": f"{3.14 * 5**2 * 4:.0f} cm³",
    "cono de radio 3 cm y altura 4 cm": f"{3.14 * 3**2 * 4 / 3:.2f} cm³".replace(".", ","),
    "esfera tiene radio 6 cm": f"{4 / 3 * 3.14 * 6**3:.2f} cm³".replace(".", ","),
    "paralelepípedo mide 6 cm, 4 cm y 3 cm": f"{2 * (6 * 4 + 6 * 3 + 4 * 3)} cm²",
    "base triangular de 6 cm de base y 4 cm de altura": f"{6 * 4 // 2 * 10} cm³",
    "estanque cilíndrico tiene 2 m de radio": f"{3.14 * 2**2 * 3:.2f} m³".replace(".", ","),
    "arista de un cubo se triplica": str(3**3),
    "cubo tiene un volumen de 64 cm³": f"{round(64 ** (1 / 3))} cm",
    "cilindro tiene un volumen de 502,4 cm³": f"{round(502.4 / (3.14 * 4**2))} cm",
    "aristas tiene un prisma de base triangular": str(3 * 3),
    "caras tiene una pirámide de base cuadrada": str(1 + 4),
    "cubos de 5 cm de arista caben": f"{20 * 15 * 10 // 5**3} cubos",
    "área total de un cilindro de radio 3 cm y altura 7 cm": (
        f"{2 * 3.14 * 3**2 + 2 * 3.14 * 3 * 7:.1f} cm²".replace(".", ",")
    ),
    "pirámide de base cuadrada de lado 6 cm y altura 10 cm": f"{6**2 * 10 // 3} cm³",
    "duplica la altura de un cilindro": str(2),
    # ================= LOTE 8 — eje PROBABILIDAD Y ESTADÍSTICA =================
    "media de los datos 5, 10, 15 y 20": f"{(5 + 10 + 15 + 20) / 4:.1f}".replace(".", ","),
    "mediana de los datos 2, 8, 4, 10 y 6": str(sorted([2, 8, 4, 10, 6])[2]),
    "moda del conjunto 1, 3, 3, 5, 8 y 3": str(Counter([1, 3, 3, 5, 8, 3]).most_common(1)[0][0]),
    "rango del conjunto 8, 15, 3, 22 y 11": str(max(8, 15, 3, 22, 11) - min(8, 15, 3, 22, 11)),
    "promedio de 12, 15 y 18": str((12 + 15 + 18) // 3),
    "mediana de los datos 4, 9, 2, 7, 6 y 11": (
        f"{(sorted([4, 9, 2, 7, 6, 11])[2] + sorted([4, 9, 2, 7, 6, 11])[3]) / 2:.1f}".replace(".", ",")
    ),
    "notas de un estudiante fueron 4,0": f"{(4 + 5 + 6 + 7 + 3) / 5:.1f}".replace(".", ","),
    "6 datos tiene media 10": str(6 * 10 - (8 + 9 + 11 + 12 + 13)),
    "5 estudiantes obtuvieron nota 4": f"{(5 * 4 + 3 * 5 + 2 * 6) / 10:.1f}".replace(".", ","),
    "rango del conjunto 45, 12, 78, 33 y 90": str(max(45, 12, 78, 33, 90) - min(45, 12, 78, 33, 90)),
    "se les suma 5, ¿qué ocurre con su media": str(5),
    "promedio de 5 números es 12": str(5 * 12 - 4 * 13),
    "promedio final sea 5,5": f"{4 * 5.5 - (5.0 + 6.0 + 4.5):.1f}".replace(".", ","),
    "moda del conjunto 2, 4, 4, 6, 6 y 8": "4 y 6",
    "primeros cinco números pares positivos": str((2 + 4 + 6 + 8 + 10) // 5),
    "mediana de 15, 22, 8, 19, 30, 12 y 25": str(sorted([15, 22, 8, 19, 30, 12, 25])[3]),
    "cuatro personas ganan $400.000": f"${(4 * 400000 + 2000000) // 5:,}".replace(",", "."),
    "rango de los datos 3,5": f"{9.8 - 3.5:.1f}".replace(".", ","),
    "dato exactamente igual a la media": "No cambia",
    "promedio de 3, 5, 7, 9 y 11": str((3 + 5 + 7 + 9 + 11) // 5),
    # --- técnicas de conteo ---
    "ordenar 3 personas en una fila": str(factorial(3)),
    "ordenar 5 libros diferentes en un estante": str(factorial(5)),
    "5 entradas y 3 postres": str(5 * 3),
    "4 camisas y 3 corbatas": str(4 * 3),
    "letras de la palabra SOL": str(factorial(3)),
    "comité de 3 personas a partir de un grupo de 5": str(comb(5, 3)),
    "elegir 2 personas de un grupo de 8": str(comb(8, 2)),
    "carrera con 5 corredores": str(5 * 4 * 3),
    "2 cifras distintas se pueden formar usando los dígitos 1, 2, 3 y 4": str(4 * 3),
    "patente se forma con 3 letras": f"{26**3:,}".replace(",", "."),
    "3 entradas, 4 platos de fondo y 2 postres": str(3 * 4 * 2),
    "subconjuntos de 2 elementos tiene un conjunto de 6": str(comb(6, 2)),
    "letras de la palabra PERRO": str(factorial(5) // factorial(2)),
    "comité de 4 personas de un grupo de 7": str(comb(7, 4)),
    "plantel de 10 jugadores": str(comb(10, 5)),
    "4 cifras distintas se pueden formar con los dígitos del 0 al 9": f"{9 * 9 * 8 * 7:,}".replace(",", "."),
    "claves distintas de 4 dígitos": f"{10**4:,}".replace(",", "."),
    "reunión de 8 personas": str(comb(8, 2)),
    "ordenar 7 personas en una fila": f"{factorial(7):,}".replace(",", "."),
    "6 hombres y 4 mujeres": str(comb(6, 2) * comb(4, 2)),
}


def _norm(t: str) -> str:
    """Normaliza para comparar: el banco usa el signo menos U+2212, no el guion."""
    return t.replace("\u2212", "-").replace("\u00a0", " ").strip()


def _norm_numero(t: str) -> str:
    """Normaliza la coma decimal antes de comparar.

    El banco escribe los decimales como se escriben en Chile —"0,5"— y Python
    los calcula como "0.5". Es el mismo número escrito distinto, no un error de
    aritmética, y sin esto el verificador reportaría fallas donde no las hay.
    """
    return _norm(t).replace(",", ".")


def _valores_del_texto(texto: str) -> set[Fraction]:
    """Todos los números que aparecen en un texto, como valores exactos.

    Compara VALOR y no cadena, porque el mismo número se escribe de varias
    formas legítimas en el banco: `\\frac{11}{18}` en LaTeX, `20.400` con punto
    de miles a la chilena, `27{,}44` con coma decimal. Buscar el string "11/18"
    dentro de un texto que dice `\\frac{11}{18}` falla sin que nada esté malo.
    """
    t = _norm(texto)

    valores: set[Fraction] = set()

    # Fracciones LaTeX: \frac{a}{b} y \dfrac{a}{b}.
    for num, den in re.findall(r"\\d?frac\{(-?\d+)\}\{(-?\d+)\}", t):
        if int(den) != 0:
            valores.add(Fraction(int(num), int(den)))

    # Fracciones escritas con barra.
    for num, den in re.findall(r"(-?\d+)\s*/\s*(\d+)", t):
        if int(den) != 0:
            valores.add(Fraction(int(num), int(den)))

    # Números sueltos. El punto separa miles y la coma decimales (formato
    # chileno); en LaTeX la coma decimal se escribe {,}.
    limpio = t.replace("{,}", ",")
    for crudo in re.findall(r"-?\d[\d.]*(?:,\d+)?", limpio):
        sin_miles = crudo.replace(".", "") if "," in crudo or crudo.count(".") >= 1 else crudo
        sin_miles = sin_miles.replace(",", ".")
        try:
            valores.add(Fraction(sin_miles))
        except (ValueError, ZeroDivisionError):
            continue

    return valores


def main() -> int:
    fallas: list[str] = []

    # ---- capa 1: estructura ----
    todas = QUESTIONS + QUESTIONS_LECTORA + QUESTIONS_CIENCIAS + QUESTIONS_HISTORIA

    # ---- capa 3: Competencia Lectora ----
    # Una pregunta de lectura sin su texto es una pregunta que nadie puede
    # responder, y un texto sin preguntas es peso muerto en el ensayo.
    con_fuente = QUESTIONS_LECTORA + [q for q in QUESTIONS_HISTORIA if q.get("passage")]
    for q in con_fuente:
        clave = q.get("passage")
        if not clave:
            fallas.append(f"pregunta de lectora sin texto asociado: {q['stem'][:60]}")
        elif clave not in CLAVES_PASAJE:
            fallas.append(f"apunta a un texto inexistente '{clave}': {q['stem'][:60]}")

    usados = {q.get("passage") for q in con_fuente}
    for clave in CLAVES_PASAJE - usados:
        fallas.append(f"el texto '{clave}' no tiene ninguna pregunta asociada")

    # Un texto continuo corto no da para preguntar; una tabla o infografía sí,
    # porque su densidad está en los datos y no en la extensión.
    for p in TODOS_LOS_PASAJES:
        minimo = 150 if p["kind"] == "discontinuo" else 400
        if len(p["body"]) < minimo:
            fallas.append(
                f"texto '{p['key']}' demasiado corto para su tipo "
                f"({len(p['body'])} caracteres, mínimo {minimo})"
            )
        if not p.get("source_note"):
            fallas.append(f"texto '{p['key']}' sin nota de origen")

    vistos: Counter[str] = Counter()
    for q in todas:
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
    por_stem = {q["stem"]: q for q in todas}
    comprobadas = 0
    for fragmento, esperado in {**COMPROBACIONES, **COMPROBACIONES_CIENCIAS}.items():
        candidatas = [s for s in por_stem if fragmento in s]
        if len(candidatas) != 1:
            fallas.append(
                f"el fragmento '{fragmento}' calza con {len(candidatas)} enunciados"
            )
            continue
        q = por_stem[candidatas[0]]
        correcta = next(a["text"] for a in q["alternatives"] if a["is_correct"])
        if _norm_numero(esperado) not in _norm_numero(correcta):
            fallas.append(
                f"aritmética: '{fragmento}' → esperado '{esperado}', "
                f"la marcada correcta dice '{correcta}'"
            )
        comprobadas += 1

    # ---- capa 4: lecciones ----
    # La lección es lo que el estudiante lee ANTES de practicar, y se la cree.
    # Vale la misma exigencia que una pregunta.
    for codigo, leccion in LESSONS.items():
        if codigo not in CODIGOS:
            fallas.append(f"lección de un nodo inexistente: '{codigo}'")
        for campo in ("intro", "theory", "example_statement"):
            if not leccion.get(campo, "").strip():
                fallas.append(f"lección '{codigo}' sin {campo}")
        pasos = leccion.get("example_steps", [])
        if len(pasos) < 2:
            fallas.append(f"lección '{codigo}' tiene {len(pasos)} paso(s); mínimo 2")
        for i, paso in enumerate(pasos, 1):
            # El "porque" es la razón de ser del formato: sin él queda una
            # receta para copiar, no una explicación.
            if not paso.get("accion", "").strip():
                fallas.append(f"lección '{codigo}', paso {i} sin acción")
            if not paso.get("porque", "").strip():
                fallas.append(f"lección '{codigo}', paso {i} sin el porqué")

    leidas = 0
    for codigo, esperado in RESULTADOS_LECCIONES.items():
        leccion = LESSONS.get(codigo)
        if leccion is None:
            fallas.append(f"se comprueba un resultado de '{codigo}', que no existe")
            continue
        texto = " ".join(p["accion"] for p in leccion["example_steps"])
        if esperado not in _valores_del_texto(texto):
            fallas.append(
                f"aritmética de la lección '{codigo}': el resultado recalculado "
                f"es {esperado} y no aparece en ningún paso del ejemplo"
            )
        leidas += 1

    # ---- reporte ----
    print(
        f"preguntas en el banco: {len(todas)} (matemática {len(QUESTIONS)}, "
        f"lectora {len(QUESTIONS_LECTORA)}, ciencias {len(QUESTIONS_CIENCIAS)}, "
        f"historia {len(QUESTIONS_HISTORIA)})"
    )
    print(f"textos y fuentes: {len(TODOS_LOS_PASAJES)}")
    print(f"comprobaciones aritméticas ejecutadas: {comprobadas}")
    print(f"lecciones: {len(LESSONS)} ({leidas} con resultado recalculado)")
    por_nodo = Counter(q["skill_node"] for q in todas)
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
