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

# Plantillas donde los números SÍ cambian la tarea, así que dos preguntas
# gemelas pueden llevar dificultades distintas. Cada fragmento identifica a la
# pregunta que rompe la simetría, y va con el motivo por el que la rompe.
EXCEPCIONES_DIFICULTAD = {
    "x² + 12x + 36": "raíz doble: una única solución, no dos",
    "x² − 10x + 25": "raíz doble: una única solución, no dos",
    "2x + 3y = 17": "hay que amplificar las dos ecuaciones; la gemela se reduce directo",
    "(1, 4) se rota 90°": "punto general; la gemela está sobre un eje y se ve a ojo",
    "(2, 5) se rota 180°": "punto general; la gemela está sobre un eje",
    "(4, 1) se rota 270°": "270° exige componer giros; la gemela es un cuarto de vuelta",
    "√75 + √27": "obliga a simplificar radicales; las gemelas son raíces exactas",
    "√98 − √50": "la resta obliga a simplificar radicales; la gemela son raíces exactas",
    "9^(3/2)": "exponente m/n con m>1: hay potencia y raíz; las gemelas son solo raíz",
    "√12 · √3": "exige la regla del producto de raíces; la gemela son raíces exactas",
    "0,375": "tres cifras decimales frente a dos de la gemela",
    "(2/3) ÷ (4/9)": "resultado fraccionario; la gemela da entero",
    "(3/4) ÷ (9/8)": "resultado fraccionario; la gemela da entero",
    "2, 4, 4, 6, 6 y 8": "conjunto bimodal: dos modas, no una",
}

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
    # 6 pintores por 10 dias son 60 dias-pintor; repartidos entre 4 pintores dan 15 dias.
    "alg_proporcionalidad": Fraction(6 * 10, 4),

    "num_racionales": Fraction(5, 6) - Fraction(2, 9),                # 11/18
    "num_potencias_raices": Fraction(2**5) * Fraction(1, 2**3) * 2,   # 8
    "num_porcentajes": Fraction(round(20000 * 1.20 * 0.85)),          # 20.400
    "alg_lineal": Fraction(9),                                        # x = 9
    "alg_sistemas": Fraction(7),                                      # x = 7
    "alg_cuadratica": Fraction(3),                                    # x = 2 o 3
    "alg_funciones": Fraction(3),                                     # pendiente 3
    "geo_plana": Fraction(round((8 * 5 - 3.14 * 2**2) * 100), 100),   # 27,44
    "geo_semejanza": Fraction(16 * 5**2, 2**2),                       # 100 cm²
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
    # --- Proporcionalidad (alg_proporcionalidad) ---
    # Directa: la constante es el cociente. Inversa: es el producto.
    "a x = 2 le corresponde y = 10": str(10 // 2),
    "cuando x = 4 se tiene y = 15": str(4 * 15),
    "Tres kilos de pan cuestan $4.500": f"${4500 // 3 * 5:,}".replace(",", "."),
    "consume 6 litros de bencina cada 100 kilómetros": f"{6 * 250 // 100} litros",
    "4 máquinas iguales producen 200 piezas": f"{200 // 4 * 6} piezas",
    "receta para 4 personas lleva 300 gramos": f"{300 // 4 * 6} gramos",
    "llena 12 litros en 3 minutos": f"{12 // 3 * 8} litros",
    "Ocho cuadernos iguales cuestan $12.000": f"${12000 // 8 * 3:,}".replace(",", "."),
    "recorre un trayecto en 6 horas viajando a 60 km/h": f"{60 * 6 // 90} horas",
    "alcanza para 20 animales durante 12 días": f"{20 * 12 // 30} días",
    "les corresponden y igual a 7, 14, 21": str(7 * 4),
    "les corresponden y igual a 18, 12, 9": str(2 * 18 // 6),
    "y vale 12 cuando x vale 4": str(12 // 4 * 7),
    "y vale 9 cuando x vale 8": str(8 * 9 // 12),
    "imprime 90 páginas en 4 minutos": f"{round(315 / (90 / 4))} minutos",
    "15 metros de cable cuestan $27.000": f"{45000 // (27000 // 15)} metros",
    "llena con 6 llaves iguales en 20 minutos": f"{6 * 20 // 5} minutos",
    "3 partes de agua por cada 2 partes de concentrado": f"{750 * 3 // 2:,}".replace(",", ".") + " mililitros",
    "pasa por el punto (4, 10)": str(10 / 4).replace(".", ","),
    "La primera tiene 30 dientes y da 40 vueltas": f"{30 * 40 // 24} vueltas",
    "llena con 3 llaves iguales en 4 horas": f"{round(3 * 4 / 1.5)} llaves",
    "van 12 personas, cada una paga $9.000": f"${12 * 9000 // 18:,}".replace(",", "."),
    "Seis máquinas trabajando 8 horas diarias producen 480 piezas": f"{480 // (6 * 8) * 9 * 5} piezas",
    "Ocho obreros levantan 240 metros de muro en 6 días": f"{300 // (12 * (240 // (8 * 6)))} días",
    "$180.000 entre tres personas en partes directamente proporcionales a 2, 3 y 4": f"${180000 // 9 * 4:,}".replace(",", "."),
    "$120.000 entre tres personas en partes inversamente proporcionales a 2, 3 y 6": f"${120000 // 6 * 3:,}".replace(",", "."),
    "Cinco tractores aran un campo en 12 días": f"{5 * 12 * 6 // (6 * 10)} días",
    "4 ayudantes trasladan 600 ladrillos en 3 horas": f"{1000 // (600 // (4 * 3)) // 2} ayudantes",
    "45 metros cuadrados se necesitan 6 litros": str(45 / 6).replace(".", ","),
    "saca 240 copias en 6 minutos y otra saca 200 copias en 8 minutos": f"{(240 // 6 + 200 // 8) * 10} copias",
    "rinde 12 metros cuadrados con una mano y 8 metros cuadrados": f"{96 // 8} litros",
    "Con 800 gramos de fruta se usan 200 gramos de azúcar": f"{1500 * 800 // (800 + 200):,}".replace(",", ".") + " gramos",
    "llave que lo llena en 6 horas y un desagüe que lo vacía en 12 horas": f"{1 // (Fraction(1, 6) - Fraction(1, 12))} horas",
    "Con 15 participantes cada uno paga $24.000": f"{15 * 24000 // 18000} participantes",
    "150 kilómetros aparecen a 6 centímetros": str(90 * 6 / 150).replace(".", ",") + " centímetros",
    "a 2 horas le corresponden 50 litros": f"{50 // 2 * 9} litros",
    "cuando x vale 5, y vale 24": str(5 * 24 // 8),
    # --- Porcentajes nuevos ---
    "25% de descuento y, al pagar con cierta tarjeta": f"{100 - 100 * 0.75 * 0.9:.1f}%".replace(".", ","),
    "¿Qué porcentaje de descuento hay que aplicarle al nuevo precio": f"{round(25 / 125 * 100)}%",
    "el 60% son mujeres": f"{round(0.6 * 25 + 0.4 * 50)}%",
    "compra un producto en $24.000 y quiere venderlo ganando un 25% sobre el precio de venta": f"${round(24000 / 0.75):,}".replace(",", "."),
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
    "hoja se dobla por la mitad 3 veces": str(2**3 * 2**4),
    "√81 − √16": str(int(sqrt(81) - sqrt(16))),
    "(3⁵ · 3²) ÷ 3⁴": str(3**5 * 3**2 // 3**4),
    "reduce el tamaño de una figura a la quinta parte": str(Fraction(1, 5**2)),
    "población de insectos se duplica cada día": str(5 if 2**5 == 32 else None),
    # --- porcentajes ---
    "15% de 240": str(int(0.15 * 240)),
    "18.000 y se le aplica un descuento del 25%": f"{int(18000 * 0.75):,}".replace(",", "."),
    "40 estudiantes, 24 son mujeres": f"{int(24 / 40 * 100)}%",
    "sube un 20% y después baja un 20%": "4" if abs(1 - 1.2 * 0.8 - 0.04) < 1e-9 else "?",
    "Ocho trabajadores construyen": str(8 * 15 // 12),
    # --- álgebra ---
    "compra 5 sacos de cemento y 3 de arena": f"{5 - 2}a + {3 + 7}b",
    "a + b = 9 y a · b = 20": str(9**2 - 2 * 20),
    "panadería vende 4 bandejas iguales de pan": str((13 + 7) // 4),
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
    "cilindro tiene 8 cm de diámetro y 15 cm de altura": f"{3.14 * (8 // 2) ** 2 * 15:.1f} cm³".replace(".", ","),
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
    # Lleva los dígitos porque hay varias preguntas de "3 cifras distintas".
    "3 cifras distintas se pueden formar usando los dígitos 1, 2, 3, 4 y 5": str(5 * 4 * 3),
    "6 personas se debe elegir un comité de 2": str(comb(6, 2)),
    "2 letras seguidas de 3 dígitos": f"{26**2 * 10**3:,}".replace(",", "."),
    "3 poleras y 4 pantalones": str(3 * 4),
    "número primo": str(Fraction(3, 6)),
    "7 fichas blancas y 5 negras": str(Fraction(5, 12)),
    "Se lanzan dos monedas. ¿Cuál": str(Fraction(1, 4)),
    # Lleva la condición porque hay varias preguntas sobre la baraja de 52.
    "sea un as o una carta de corazones": f"{4 + 13 - 1}/52",
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
    # --- perímetros y áreas: segunda tanda ---
    # Aplicación directa de fórmula.
    "cada pieza es un paralelogramo de 14 cm": str(14 * 6),
    "bases paralelas miden 9 m y 5 m": str((9 + 5) // 2 * 6),
    "varillas, que corresponden a las diagonales": f"{70 * 50 // 2:,}".replace(",", "."),
    "baldosa cuadrada mide 25 cm de lado": str(25**2),
    "mantel cuadrado de 130 cm de lado": str(4 * 130),
    "vela de un velero de juguete": str(16 * 9 // 2),
    "huerto rectangular mide 20 m de largo": str(20 * 7),
    "cuadro rectangular mide 17 cm": str(2 * (17 + 11)),
    "triángulo equilátero de 15 cm de lado": str(3 * 15),
    "tapa circular de un frasco": str(round(3.14 * 3**2, 2)).replace(".", ","),
    "platillo circular tiene 10 cm de radio": str(round(2 * 3.14 * 10, 2)).replace(".", ","),
    "cartel tiene forma de rombo": str(4 * 8),
    "pizza familiar tiene 30 cm de diámetro": str(round(3.14 * (30 // 2) ** 2, 2)).replace(".", ","),
    # Casos inversos: se da el área y se pide una medida.
    "vitral tiene forma de trapecio y su área": str(60 // ((8 + 12) // 2)),
    "lámina con forma de paralelogramo": str(96 // 8),
    "rombo tiene un área de 84 cm²": str(2 * 84 // 14),
    "área de una mesa circular es 200,96": str(round((200.96 / 3.14) ** 0.5)),
    "contorno de un plato circular mide 37,68": str(round(37.68 / (2 * 3.14))),
    # Figuras compuestas, unidades y contexto.
    "living tiene forma de L": str(6 * 4 + 3 * 2),
    "ventana tiene forma de semicírculo de 6 cm": str(round(3.14 * 6**2 / 2, 2)).replace(".", ","),
    # 12 m² de piso divididos por 0,04 m² de baldosa; en float hay que redondear.
    "baldosas cuadradas de 20 cm de lado": str(round((4 * 3) / (0.2 * 0.2))),
    "Pintar una pared cuesta $3.500": f"{round(5 * 2.4) * 3500:,}".replace(",", "."),
    "dos lados perpendiculares miden 9 m y 12 m": str(9 * 12 // 2),
    "plancha rectangular de 20 cm por 12 cm": str(20 * 12 - 4 * 3**2),
    "bases miden 25 m y 15 m, y su altura 12 m": f"{(25 + 15) // 2 * 12 * 8000:,}".replace(",", "."),
    # Anillos: restar áreas, nunca radios.
    "argolla metálica": str(round(3.14 * (10**2 - 6**2), 2)).replace(".", ","),
    "piscina circular de 4 m de radio está rodeada": str(round(3.14 * ((4 + 1) ** 2 - 4**2), 2)).replace(".", ","),
    "borde decorativo de 10 cm de ancho hacia adentro": str(round((3 - 2 * 0.1) * (2 - 2 * 0.1), 2)).replace(".", ","),
    # Escala y semejanza: el factor lineal va al cuadrado para las superficies.
    # Los fragmentos llevan el objeto porque hay varias preguntas por escala.
    "1 : 100, una sala aparece": str(5 * 4),
    "1 : 50, una bodega ocupa": str(30 * 50**2 / 10_000).replace(".", ","),
    "razón entre sus lados es 2 : 5": str(12 * 5**2 // 2**2),
    # Ecuación previa antes de poder calcular el área.
    "perímetro de 70 m y su largo mide 5 m más": str((70 // 2 - 5) // 2 * ((70 // 2 - 5) // 2 + 5)),
    "mismo perímetro: 40 cm": str((40 // 4) ** 2 - 14 * 6),
    # Efecto de escalar una dimensión sobre el área.
    "lado de un cuadrado se triplica": str(3**2),
    "radio de un círculo aumenta en un 50%": str(round((1.5**2 - 1) * 100)),
    # --- Teorema de Pitágoras: segunda tanda ---
    # Hipotenusa a partir de los dos catetos.
    "jardín rectangular mide 12 m de ancho y 16 m": str(round((12**2 + 16**2) ** 0.5)),
    "rampa de acceso sube 7 m de altura": str(round((7**2 + 24**2) ** 0.5)),
    "tirante de acero": str(round((18**2 + 24**2) ** 0.5)),
    "catetos que miden 30 cm y 40 cm": str(round((30**2 + 40**2) ** 0.5)),
    "pantalla rectangular mide 21 cm de ancho": str(round((21**2 + 28**2) ** 0.5)),
    "volantín se eleva a 40 m de altura": str(round((40**2 + 9**2) ** 0.5)),
    "catetos de 33 cm y 44 cm": str(round((33**2 + 44**2) ** 0.5)),
    "sube 12 cm por la pared y avanza 35 cm": str(round((12**2 + 35**2) ** 0.5)),
    "pantalla mide 48 cm de ancho y 36 cm de alto": str(round((48**2 + 36**2) ** 0.5)),
    # Cateto a partir de la hipotenusa: los cuadrados se restan.
    "hipotenusa mide 20 cm y uno de sus catetos mide 12 cm": str(round((20**2 - 12**2) ** 0.5)),
    "hipotenusa mide 34 cm y un cateto mide 16 cm": str(round((34**2 - 16**2) ** 0.5)),
    "hipotenusa mide 53 cm y un cateto mide 28 cm": str(round((53**2 - 28**2) ** 0.5)),
    "la hipotenusa mide 2 cm más que ese cateto": str(round(((8 + 2) ** 2 - 8**2) ** 0.5)),
    # Resultados irracionales: lado · √2 en el cuadrado, lado · √3 / 2 en el equilátero.
    "mantel cuadrado mide 7 cm de lado": f"{7}√2",
    "triángulo equilátero de 12 cm de lado": f"{12 // 2}√3",
    "triángulo equilátero de 6 cm de lado": f"{6 // 2}√3",
    # Distancia entre dos puntos del plano cartesiano.
    "A(1, 2) y B(9, 8)": str(round(((9 - 1) ** 2 + (8 - 2) ** 2) ** 0.5)),
    "P(−3, 1) y Q(2, 13)": str(round(((2 - (-3)) ** 2 + (13 - 1) ** 2) ** 0.5)),
    # Pitágoras sobre las mitades de una figura.
    "diagonales que miden 24 cm y 10 cm": str(round(((24 // 2) ** 2 + (10 // 2) ** 2) ** 0.5)),
    "dos lados iguales de 13 cm y una base de 10 cm": str(round((13**2 - (10 // 2) ** 2) ** 0.5)),
    "trapecio isósceles tiene bases de 20 cm y 12 cm": str(round((5**2 - ((20 - 12) // 2) ** 2) ** 0.5)),
    "circunferencia de 13 cm de radio se traza una cuerda": str(2 * round((13**2 - 5**2) ** 0.5)),
    # Pitágoras como paso intermedio de otro cálculo.
    "área de un triángulo rectángulo cuyos catetos miden 10 cm y 24 cm": str(10 * 24 // 2),
    "cercar un terreno con forma de triángulo rectángulo": str(9 + 12 + round((9**2 + 12**2) ** 0.5)),
    "antena de 24 m se sujeta con dos cables": str(2 * round((24**2 + 7**2) ** 0.5)),
    "hipotenusa de 25 cm y uno de sus catetos mide 15 cm": str(15 * round((25**2 - 15**2) ** 0.5) // 2),
    "área de un triángulo rectángulo es 54 cm²": str(round((12**2 + (2 * 54 // 12) ** 2) ** 0.5)),
    "cuadrado y un triángulo rectángulo de catetos 6 cm y 8 cm": str(((6 + 8 + round((6**2 + 8**2) ** 0.5)) // 4) ** 2),
    "diagonal de un cuadrado mide 8√2 cm": str(8**2),
    "barco navega 24 km hacia el norte": str(round((24**2 + 45**2) ** 0.5)),
    "torre proyecta una sombra de 24 m": str(round((26**2 - 24**2) ** 0.5)),
    # La escalera conserva su largo: misma hipotenusa en las dos posiciones.
    "escalera de 25 m apoyada en una pared vertical llega a 24 m": str(
        round((25**2 - (round((25**2 - 24**2) ** 0.5) + 8) ** 2) ** 0.5)
    ),
    # Un cateto es el doble del otro: 5x² = 45.
    "hipotenusa mide √45 cm": str(round((45 / 5) ** 0.5)),
    # Perímetro y diagonal: (l+a)² = l² + a² + 2·área.
    "perímetro de 34 cm y su diagonal mide 13 cm": str(((34 // 2) ** 2 - 13**2) // 2),
    # El único trío que no cumple el teorema.
    "NO puede corresponder a los lados": next(
        f"{a}, {b} y {c}"
        for a, b, c in [(10, 24, 26), (12, 16, 20), (8, 15, 17), (5, 6, 8)]
        if a**2 + b**2 != c**2
    ),
    # --- transformaciones isométricas: segunda tanda ---
    # Traslación: se suma el vector componente a componente.
    "videojuego, un personaje está en la casilla (7, 3)": f"({7 + (-3)}, {3 + 5})",
    "dron se encuentra en el punto (−4, 2)": f"({-4 + 6}, {2 + (-5)})",
    "una caja está en el punto (5, 6)": f"({5 + 0}, {6 + (-4)})",
    "punto (−7, −1) se traslada según el vector (7, 1)": f"({-7 + 7}, {-1 + 1})",
    "robot parte del punto (2, 1)": f"({2 + 4 + (-1)}, {1 + 3 + 2})",
    "nueva posición del vértice (5, 1)": f"({5 + 3}, {1 + (-2)})",
    # Reflexión en los ejes: cambia de signo una sola coordenada.
    "punto (9, −4) al reflejarlo respecto del eje X": f"(9, {0 - (-4)})",
    "punto (−8, 5) al reflejarlo respecto del eje Y": f"({0 - (-8)}, 5)",
    "punto (3, 8) al reflejarlo respecto del eje Y": f"({0 - 3}, 8)",
    "punto (−5, −6) al reflejarlo respecto del eje X": f"({-5}, {0 - (-6)})",
    "punto (2, 9) al reflejarlo respecto del origen": f"({-2}, {-9})",
    # Reflexión en rectas que no son los ejes: el punto queda al otro lado, a igual distancia.
    "recta vertical x = 6": f"({2 * 6 - 4}, 3)",
    "recta horizontal y = 5": f"(5, {2 * 5 - 2})",
    # Reflexión en y = x: se intercambian las coordenadas.
    "punto (6, −1) se refleja respecto de la recta y = x": f"({-1}, {6})",
    # Rotaciones: 90° antihorario (x,y)->(-y,x); horario (x,y)->(y,-x); 180° (-x,-y).
    "punto (6, 0) se rota 180°": f"({-6}, {0})",
    "ficha ubicada en (0, 7)": f"({7}, {-0})",
    "punto (5, −2) se rota 90° en sentido antihorario": f"({0 - (-2)}, {5})",
    "punto (−3, 6) se rota 90° en sentido horario": f"({6}, {0 - (-3)})",
    # 270° antihorario equivale a 90° horario.
    "punto (7, −4) se rota 270°": f"({-4}, {-7})",
    # Vector entre dos puntos: llegada menos partida.
    "traslada el punto (1, 4) hasta el punto (6, 9)": f"({6 - 1}, {9 - 4})",
    "traslada el punto (−2, 5) hasta el punto (3, −1)": f"({3 - (-2)}, {-1 - 5})",
    "triángulo tiene un vértice en (1, 2)": f"({0 - 1}, {0 - 2})",
    # Problema inverso: se conoce la llegada y se busca la partida.
    "trasladó según el vector (5, −3) y quedó en (2, 4)": f"({2 - 5}, {4 - (-3)})",
    "traslada según un vector (a, b) y queda en (3, 9)": str((3 - 7) + (9 - 2)),
    # Composiciones.
    "punto (−6, 2) se refleja respecto del eje X y el resultado se traslada": f"({-6 + 3}, {-2 + 4})",
    "punto (8, 5) se rota 180° en torno al origen y el resultado se refleja": f"({0 - (-8)}, {-5})",
    "punto (3, −2) se rota 90° en sentido antihorario en torno al origen y el resultado": f"({0 - (-2) + (-1)}, {3 + 5})",
    "punto (−5, 3) se refleja primero respecto del eje X": f"({0 - (-5)}, {-3})",
    "dónde queda el vértice (4, 4)": f"({-4}, {4})",
    # Módulo de un vector: Pitágoras sobre sus componentes.
    "módulo del vector de traslación (9, 12)": str(round((9**2 + 12**2) ** 0.5)),
    # La reflexión es isometría: el perímetro no cambia.
    "vértices en A(2, 1), B(6, 1) y C(2, 4)": str(
        (6 - 2) + (4 - 1) + round(((6 - 2) ** 2 + (4 - 1) ** 2) ** 0.5)
    ),
    # --- cuerpos geométricos: segunda tanda ---
    # Volumen de cubos y paralelepípedos: producto de las tres dimensiones.
    "¿Cuál es el volumen de un cubo de 6 cm de arista?": str(6**3),
    "caja tiene 8 cm de largo, 5 cm de ancho": str(8 * 5 * 3),
    "cubo de 10 cm de arista": f"{10**3:,}".replace(",", "."),
    "contenedor mide 10 cm de largo": str(10 * 6 * 4),
    "caja de herramientas mide 12 cm": str(12 * 5 * 3),
    "base cuadrada de 5 cm de lado y una altura de 12 cm": str(5**2 * 12),
    "piscina rectangular mide 8 m de largo": str(round(8 * 4 * 1.5)),
    # Área total: seis caras en el cubo, tres pares distintos en el paralelepípedo.
    "área total de un cubo de 5 cm de arista": str(6 * 5**2),
    "área total de un cubo de 2 cm de arista": str(6 * 2**2),
    "caja mide 7 cm de largo, 4 cm de ancho": str(2 * (7 * 4 + 7 * 3 + 4 * 3)),
    "paralelepípedo de 10 cm de largo, 6 cm de ancho y 4 cm de alto": str(2 * (10 * 6 + 10 * 4 + 6 * 4)),
    # Cilindros: área de la base por la altura; la lateral es un rectángulo desenrollado.
    "cilindro de 2 cm de radio y 5 cm de altura": str(round(3.14 * 2**2 * 5, 2)).replace(".", ","),
    "cilindro de 10 cm de radio y 2 cm de altura": str(round(3.14 * 10**2 * 2)),
    "área lateral de un cilindro de 5 cm de radio": str(round(2 * 3.14 * 5 * 10)),
    "estanque cilíndrico tiene 3 m de radio": str(round(3.14 * 3**2 * 4, 2)).replace(".", ","),
    "área total de un cilindro de 2 cm de radio y 8 cm de altura": str(
        round(2 * 3.14 * 2**2 + 2 * 3.14 * 2 * 8, 2)
    ).replace(".", ","),
    "lata cilíndrica cerrada tiene 5 cm de radio": str(
        round(2 * 3.14 * 5**2 + 2 * 3.14 * 5 * 8, 2)
    ).replace(".", ","),
    # Elementos de los cuerpos.
    "¿Cuántas caras tiene un paralelepípedo?": str(3 * 2),
    "¿Cuántas aristas tiene un paralelepípedo?": str(4 * 3),
    "esquinera plástica en cada uno de sus vértices": str(4 * 2),
    # Casos inversos: se da el volumen o el área y se pide una medida.
    "cubo tiene un volumen de 216 cm³": str(round(216 ** (1 / 3))),
    "volumen de 240 cm³ y su base mide 8 cm por 5 cm": str(240 // (8 * 5)),
    "cilindro tiene un volumen de 471 cm³": str(round((471 / (3.14 * 6)) ** 0.5)),
    "área total de un cubo es 96 cm²": str(round((96 / 6) ** 0.5)),
    "cilindro tiene un volumen de 1.256 cm³": str(round(1256 / (3.14 * 10**2))),
    # El área total da la altura, y recién ahí sale el volumen.
    "base cuadrada de 4 cm de lado y un área total de 160 cm²": str(
        4**2 * ((160 - 2 * 4**2) // (4 * 4))
    ),
    # Cuántas piezas caben: se dividen volúmenes, no medidas lineales.
    "cajas cúbicas de 2 cm de arista caben": str((8 * 6 * 4) // 2**3),
    "cubo de 6 cm de arista se corta en cubitos": str(6**3 // 2**3),
    "caja mide 30 cm × 20 cm × 15 cm": str(30 * 20 * 15 // 5**3),
    # Capacidad: 1 litro son 1.000 cm³.
    "50 cm de largo, 40 cm de ancho y 30 cm de alto": str(50 * 40 * 30 // 1000),
    "bidón cilíndrico tiene 20 cm de radio": str(round(3.14 * 20**2 * 50 / 1000, 2)).replace(".", ","),
    "tres quintas partes de su capacidad": str(round(3.14 * 2**2 * 5 * 3 / 5, 2)).replace(".", ","),
    # Superficie a pintar sin tapa: la base va una sola vez.
    "pintar por fuera una caja sin tapa": f"{(5 * 4 + 2 * 5 * 3 + 2 * 4 * 3) * 200:,}".replace(",", "."),
    # Escalar dimensiones: el factor va al cuadrado o al cubo según de qué dependa.
    "duplica el radio de un cilindro": f"Por {2**2}",
    "duplican el largo, el ancho y el alto": f"Por {2**3}",
    "arista de un cubo aumenta en un 50%": str(round((1.5**3 - 1) * 100, 1)).replace(".", ","),
    # --- enteros y racionales: segunda tanda ---
    # Operatoria con enteros negativos, que es lo que el nodo no cubría.
    "temperatura en una ciudad era de −3 °C": str(-3 - 5),
    "resultado de −7 + 12": str(-7 + 12),
    "resultado de −4 · (−6)": str(-4 * -6),
    "resultado de −20 ÷ 5": str(-20 // 5),
    # 8 − (−3) se resuelve como 8 + 3: restar un negativo suma.
    "resultado de 8 − (−3)": str(8 + 3),
    "buzo se encuentra a 12 metros bajo": str(-12 + 5),
    "resultado de −6 + 4 − (−9)": str(-6 + 4 + 9),
    "resultado de (−3)² − (−3)": str((-3) ** 2 + 3),
    "saldo de −45.000 pesos": f"{-45_000 + 70_000:,}".replace(",", "."),
    "resultado de (−5) · 3 + 20 ÷ (−4)": str(-5 * 3 + 20 // -4),
    "pasó de −8 °C en la madrugada a 6 °C": str(6 + 8),
    "resultado de −3 · (5 − 8) + (−4)²": str(-3 * (5 - 8) + (-4) ** 2),
    "termómetro marcaba −6 °C a las 6": str(-6 + (11 - 6) * 2),
    # Orden: con negativos la comparación se invierte respecto de los valores.
    "es el menor: −5, −12, 3 o 0": str(min(-5, -12, 3, 0)),
    "mayor: −2/3 o −3/5": str(max(Fraction(-2, 3), Fraction(-3, 5))),
    "Ordena de menor a mayor las fracciones −1/2": ", ".join(
        str(f) for f in sorted([Fraction(-1, 2), Fraction(-3, 4), Fraction(1, 4)])
    ),
    "Ordena de menor a mayor los números −0,6": ", ".join(
        t for _, t in sorted([(Fraction(-2, 3), "-2/3"), (Fraction(-3, 5), "-0,6"), (Fraction(-29, 50), "-0,58")])
    ),
    "¿Cuántos números enteros hay entre −4 y 3": str(len(range(-4 + 1, 3))),
    # Paso de decimal a fracción irreducible.
    "0,75 como fracción irreducible": str(Fraction(75, 100)),
    "0,375 como fracción irreducible": str(Fraction(375, 1000)),
    "resultado de 1,25 + 3/4": str(Fraction(125, 100) + Fraction(3, 4)),
    # Operatoria con fracciones, incluidas las negativas.
    "resultado de 3/5 + 1/10": str(Fraction(3, 5) + Fraction(1, 10)),
    "resultado de 2/9 × 3/8": str(Fraction(2, 9) * Fraction(3, 8)),
    "resultado de −2/3 + 1/6": str(Fraction(-2, 3) + Fraction(1, 6)),
    "resultado de (−2/5) ÷ (4/15)": str(Fraction(-2, 5) / Fraction(4, 15)),
    "resultado de (−1/2)³ + 1/4": str(Fraction(-1, 2) ** 3 + Fraction(1, 4)),
    "resultado de 2 − (−3/4) ÷ (3/2)": str(2 - Fraction(-3, 4) / Fraction(3, 2)),
    "punto medio entre −5/6 y 1/3": str((Fraction(-5, 6) + Fraction(1, 3)) / 2),
    "deuda de $120.000 ya se han pagado 3/8": f"{120_000 * 5 // 8:,}".replace(",", "."),
    # --- potencias y raíces: segunda tanda ---
    # Base racional: el exponente afecta a numerador y denominador por igual.
    "valor de (2/3)²": str(Fraction(2, 3) ** 2),
    "valor de (3/5)²": str(Fraction(3, 5) ** 2),
    "valor de (1/2)⁻¹": str(Fraction(1, 2) ** -1),
    "valor de 4⁻¹": str(Fraction(1, 4)),
    "valor de (2/5)⁻²": str(Fraction(2, 5) ** -2),
    "valor de (2/3)³ · (3/2)²": str(Fraction(2, 3) ** 3 * Fraction(3, 2) ** 2),
    # Raíces enésimas. round() porque la potencia fraccionaria en float no cae exacta.
    "valor de ∛27": str(round(27 ** (1 / 3))),
    "valor de ∛64": str(round(64 ** (1 / 3))),
    "valor de ∛(8 · 27)": str(round((8 * 27) ** (1 / 3))),
    "valor de ∛(−125)": str(-round(125 ** (1 / 3))),
    "valor de ∛(1/8)": str(Fraction(1, round(8 ** (1 / 3)))),
    "caja cúbica tiene un volumen de 343 cm³": str(round(343 ** (1 / 3))),
    # Exponente racional: el denominador es el índice y el numerador la potencia.
    "valor de 8^(1/3)": str(round(8 ** (1 / 3))),
    "valor de 16^(1/2)": str(round(16**0.5)),
    "valor de 9^(3/2)": str(round(9**0.5) ** 3),
    "valor de 27^(2/3)": str(round(27 ** (1 / 3)) ** 2),
    "valor de 16^(3/4)": str(round(16**0.25) ** 3),
    # Potencias y raíces de base entera.
    "caja con forma de cubo mide 6 centímetros de arista": str(6**3),
    "terreno cuadrado tiene una superficie de 225": str(round(225**0.5)),
    "valor de (√5)⁴": str(5 ** (4 // 2)),
    "valor de √(2⁸)": str(2 ** (8 // 2)),
    "valor de (2³ · 2⁻⁵)⁻¹": str(2 ** -(3 - 5)),
    # Propiedades de las raíces: producto, descomposición y suma de semejantes.
    "valor de √12 · √3": str(round((12 * 3) ** 0.5)),
    "valor de √200 en su forma más simple": f"{round((200 // 2) ** 0.5)}√2",
    "valor de √48 en su forma más simple": f"{round((48 // 3) ** 0.5)}√3",
    "valor de √75 + √27": f"{round((75 // 3) ** 0.5) + round((27 // 3) ** 0.5)}√3",
    # Ecuación exponencial con base fraccionaria.
    "Si (1/2)ˣ = 1/32": str(
        next(x for x in range(1, 12) if Fraction(1, 2) ** x == Fraction(1, 32))
    ),
    # Crecimiento que se duplica: es una potencia, no una multiplicación.
    "cultivo de bacterias se duplica cada hora": f"{200 * 2**6:,}".replace(",", "."),
    # --- porcentaje y proporcionalidad: segunda tanda ---
    # Porcentaje directo.
    "el 40% de 350": str(round(350 * 0.4)),
    "el 5% de 800": str(round(800 * 0.05)),
    "el 75% de 200": str(round(200 * 0.75)),
    "el 8% de 2.500": str(round(2500 * 0.08)),
    "el 150% de 60": str(round(60 * 1.5)),
    "grupo de 80 personas, el 25% usa lentes": str(round(80 * 0.25)),
    "examen tiene 80 preguntas": str(round(80 * 0.65)),
    "solución de 500 ml contiene un 12%": str(round(500 * 0.12)),
    "propina del 10% sobre una cuenta de $24.000": f"{round(24_000 * 0.1):,}".replace(",", "."),
    # Qué porcentaje representa una parte del total.
    "representa 12 de un total de 48": f"{12 * 100 // 48}%",
    "representa 45 de un total de 90": f"{45 * 100 // 90}%",
    # Aumentos y descuentos.
    "bebida cuesta $1.200 y sube un 10%": f"{round(1_200 * 1.1):,}".replace(",", "."),
    "libro cuesta $15.000 y tiene un 20% de descuento": f"{round(15_000 * 0.8):,}".replace(",", "."),
    "servicio cuesta $30.000 más IVA": f"{round(30_000 * 1.19):,}".replace(",", "."),
    "600 asistentes a un evento, el 45% son mujeres": str(round(600 * 0.55)),
    # Variación porcentual: siempre sobre el valor inicial.
    "pasó de 2.400 a 3.000 habitantes": f"{round((3000 - 2400) / 2400 * 100)}%",
    "subió de $4.000 a $5.200": f"{round((5200 - 4000) / 4000 * 100)}%",
    # Problemas inversos: se conoce el resultado y se busca el punto de partida.
    "El 30% de un número es 72": str(round(72 / 0.3)),
    "aumento del 15%, un sueldo quedó en $690.000": f"{round(690_000 / 1.15):,}".replace(",", "."),
    # Proporcionalidad directa.
    "3 cm representan 15 km": str(8 * 15 // 3),
    "6 kilos de pan cuestan $9.000": f"{10 * 9_000 // 6:,}".replace(",", "."),
    "recorre 240 km con 20 litros": str(35 * 240 // 20),
    # Proporcionalidad inversa: el producto se mantiene constante.
    "Cuatro llaves llenan un estanque en 6 horas": str(4 * 6 // 3),
    # Porcentajes encadenados: se multiplican los factores, nunca se suman.
    "10% de descuento y, sobre el precio ya rebajado, otro 10%": f"{round((1 - 0.9 * 0.9) * 100)}%",
    "el 20% del 40% de 800": str(round(800 * 0.4 * 0.2)),
    "baja un 40% y después sube un 40%": f"{round((1 - 0.6 * 1.4) * 100)}%",
    "el 80% de las personas prefiere té": f"{round(0.8 * 0.35 * 100)}%",
    # El total también cambia cuando se incorpora gente.
    "18 hombres y 12 mujeres": f"{(12 + 10) * 100 // (18 + 12 + 10)}%",
    # Comparar dos ofertas exige calcular ambos precios finales.
    "tienda A, que ofrece un 30% de descuento": "$"
    + f"{36_000 - round(50_000 * 0.7):,}".replace(",", "."),
    # Reparto proporcional: el total se parte en la suma de la razón.
    "reparten $120.000 entre dos personas en la razón 2 : 3": f"{120_000 * 3 // 5:,}".replace(",", "."),
    # --- estadística descriptiva: segunda tanda ---
    # Frecuencia relativa: la parte comparada con el total.
    "encuesta a 50 personas, 20 eligieron el cine": str(20 / 50).replace(".", ","),
    "el dato 7 aparece 5 veces sobre un total de 25": f"{5 * 100 // 25}%",
    "grupo de 40 personas, 10 tienen 20 años": str(10 / 40).replace(".", ","),
    "encuesta a 80 personas, 24 prefieren el fútbol": f"{24 * 100 // 80}%",
    "0,2, 0,35 y 0,3": str(round(1 - (0.2 + 0.35 + 0.3), 2)).replace(".", ","),
    # Tendencia central.
    "mediana de los datos 3, 6, 9, 12 y 15": str(sorted([3, 6, 9, 12, 15])[2]),
    "media de los datos 2, 4, 6, 8, 10 y 12": str((2 + 4 + 6 + 8 + 10 + 12) // 6),
    "moda del conjunto 8, 5, 8, 3, 8 y 5": str(Counter([8, 5, 8, 3, 8, 5]).most_common(1)[0][0]),
    "rango del conjunto 25, 40, 18 y 33": str(max(25, 40, 18, 33) - min(25, 40, 18, 33)),
    "media de 14, 18 y 22": str((14 + 18 + 22) // 3),
    "tres datos iguales a 5 y dos datos iguales a 10": str(3 * 5 + 2 * 10),
    "mediana de los datos 4, 4, 7 y 9": str((4 + 7) / 2).replace(".", ","),
    "mediana de los datos 5, 8, 12, 15, 18, 21, 24, 27 y 30": str(
        sorted([5, 8, 12, 15, 18, 21, 24, 27, 30])[4]
    ),
    "25 estudiantes, 8 obtuvieron nota 4": str(
        Counter([4] * 8 + [5] * 12 + [6] * 5).most_common(1)[0][0]
    ),
    # Media ponderada desde una tabla de frecuencias.
    "nota 4 la obtuvieron 6 estudiantes": str(
        round((4 * 6 + 5 * 10 + 6 * 4) / (6 + 10 + 4), 1)
    ).replace(".", ","),
    "conjunto de 8 datos tiene una media de 15": str(15 * 8),
    "4 notas cuyo promedio es 5,2": str(round(5.2 * 4, 1)).replace(".", ","),
    # Medidas de posición: cuartiles, percentiles y diagrama de cajón.
    "primer cuartil (Q1) de los datos 2, 4, 6, 8, 10, 12, 14 y 16": str((4 + 6) // 2),
    "tercer cuartil (Q3) de los datos 2, 4, 6, 8, 10, 12, 14 y 16": str((12 + 14) // 2),
    "primer cuartil es 12 y el tercer cuartil es 28": str(28 - 12),
    "rango intercuartílico de los datos 3, 5, 7, 9, 11, 13, 15 y 17": str((13 + 15) // 2 - (5 + 7) // 2),
    "200 datos, el percentil 30": str(round(200 * 0.3)),
    "20 datos ordenados, ¿cuántos datos son menores o iguales al percentil 25": str(round(20 * 0.25)),
    # Entre Q1 y Q3 vive el 50% central; sobre Q3 queda el 25%.
    "mínimo 5, Q1 = 10, mediana 15": f"{2 * 25}%",
    "mínimo 4, Q1 = 9, mediana 14": f"{100 - 75}%",
    # Criterio de dato atípico: Q3 + 1,5 veces el rango intercuartílico.
    "Q1 = 15 y Q3 = 35": str(round(35 + 1.5 * (35 - 15))),
    # Problemas de suma total: quitar o agregar datos.
    "promedio de 6 números es 20": str((20 * 6 - 30) // 5),
    "30 estudiantes tiene promedio 5,0": str(round((5.0 * 30 - 6.0 * 10) / 20, 1)).replace(".", ","),
    "media de 10 datos es 12": str((12 * 10 + 20 + 28) // (10 + 2)),
    # La mediana con una cantidad par de datos.
    "50 datos ordenados de menor a mayor": f"{50 // 2} y {50 // 2 + 1}",
    # Con un dato extremo, la mediana representa mejor que la media.
    "300, 320, 340, 360 y 2.000": str(sorted([300, 320, 340, 360, 2000])[2]),
    # Escalar los datos escala la media en el mismo factor.
    "se les multiplica por 3": f"Queda multiplicada por {3}",
    # --- técnicas de conteo: segunda tanda ---
    # Principio multiplicativo: una elección de cada grupo.
    "6 tipos de café y 4 tipos de queque": str(6 * 4),
    "5 gorros y 6 bufandas": str(5 * 6),
    "un dado de 6 caras y una moneda": str(6 * 2),
    "cerrojo de seguridad tiene 3 ruedas": str(4**3),
    "1 de 2 tipos de pan": str(2 * 3 * 2),
    "7 modelos de polera y 5 de jockey": str(7 * 5),
    "código de acceso tiene 2 dígitos": str(10**2),
    "7 rutas, y de la B a la C hay 3": str(7 * 3),
    "4 entradas, 6 platos de fondo y 3 postres": str(4 * 6 * 3),
    "3 letras seguidas de 2 dígitos": f"{26**3 * 10**2:,}".replace(",", "."),
    # Espacios muestrales, que son el denominador de una probabilidad.
    "resultados distintos se pueden obtener al lanzar dos dados": str(6**2),
    "lanzar tres monedas": str(2**3),
    "la suma es igual a 7": str(sum(1 for a in range(1, 7) for b in range(1, 7) if a + b == 7)),
    # Permutaciones: importa el orden.
    "ordenar 2 personas en una fila": str(factorial(2)),
    "ordenar 8 personas en una fila": f"{factorial(8):,}".replace(",", "."),
    "3 cifras distintas se pueden formar usando los dígitos 1, 2, 3, 4, 5 y 6": str(6 * 5 * 4),
    "carrera con 7 corredores": str(7 * 6 * 5),
    "bandera de 3 franjas": str(5 * 4 * 3),
    "4 cifras se pueden formar usando solo los dígitos 1, 2 y 3": str(3**4),
    # Permutaciones con elementos repetidos: se divide por cada repetición.
    "letras de la palabra COCO": str(factorial(4) // (factorial(2) * factorial(2))),
    "letras de la palabra BANANA": str(factorial(6) // (factorial(3) * factorial(2))),
    # Combinaciones: no importa el orden.
    "parejas distintas se pueden formar con 4 personas": str(comb(4, 2)),
    "elegir 3 personas de un grupo de 7": str(comb(7, 3)),
    "subconjuntos de 3 elementos tiene un conjunto de 8": str(comb(8, 3)),
    "2 delegados de un curso de 12": str(comb(12, 2)),
    "3 premios idénticos entre 9 personas": str(comb(9, 3)),
    # El esquema de las parejas: partidos, brindis y diagonales son lo mismo.
    "torneo participan 6 equipos": str(comb(6, 2)),
    "reunión de 10 personas": str(comb(10, 2)),
    "diagonales tiene un polígono de 8 lados": str(comb(8, 2) - 8),
    # Conteo con restricciones: se empieza por la posición restringida.
    "números pares de 2 cifras distintas": str(2 * 3),
    "0, 1, 2, 3 y 4, si el número no puede comenzar con 0": str(4 * 4 * 3),
    "3 cifras distintas y mayores que 500": str(2 * 5 * 4),
    "sentar 5 personas en una fila, si dos de ellas": str(factorial(4) * factorial(2)),
    "una persona determinada debe estar sí o sí": str(comb(9, 2)),
    "2 hombres y 3 mujeres": str(comb(5, 2) * comb(6, 3)),
    # --- reglas de las probabilidades: tercera tanda ---
    # Probabilidad simple: casos favorables sobre casos posibles.
    "3 bolitas rojas, 4 azules y 5 verdes": str(Fraction(4, 3 + 4 + 5)),
    "obtener un número menor que 3": str(Fraction(2, 6)),
    "12 lápices y 3 de ellos están malos": str(Fraction(3, 12)),
    "naipe español de 40 cartas, que tiene 4 reyes": str(Fraction(4, 40)),
    "moneda equilibrada una vez": str(Fraction(1, 2)),
    "15 fichas numeradas del 1 al 15": str(Fraction(15 // 5, 15)),
    "36 estudiantes, 27 aprobaron": str(Fraction(27, 36)),
    "dado de 8 caras numeradas del 1 al 8": str(Fraction(4, 8)),
    "tómbola hay 30 números y solo 5": str(Fraction(5, 30)),
    "12 figuras (J, Q y K": str(Fraction(12, 52)),
    # Suceso contrario.
    "gane su próximo partido es 0,45": str(round(1 - 0.45, 2)).replace(".", ","),
    "llueva mañana es 1/4": str(1 - Fraction(1, 4)),
    # Espacio muestral de dos dados: hay que contar los 36 pares.
    "suma de los puntos sea 7": str(
        Fraction(sum(1 for a in range(1, 7) for b in range(1, 7) if a + b == 7), 36)
    ),
    "suma de los puntos sea mayor que 9": str(
        Fraction(sum(1 for a in range(1, 7) for b in range(1, 7) if a + b > 9), 36)
    ),
    "obtener exactamente una cara": str(Fraction(2, 4)),
    # Regla aditiva, con y sin intersección.
    "sucesos excluyentes se sabe que P(A) = 0,5": str(round(0.5 + 0.4, 2)).replace(".", ","),
    "P(A) = 0,6, P(B) = 0,5 y P(A y B) = 0,2": str(round(0.6 + 0.5 - 0.2, 2)).replace(".", ","),
    "8 fichas numeradas del 1 al 8": str(
        Fraction(len({n for n in range(1, 9) if n % 2 == 0} | {n for n in range(1, 9) if n > 6}), 8)
    ),
    "múltiplo de 2 o un múltiplo de 3": str(
        Fraction(len({n for n in range(1, 7) if n % 2 == 0} | {n for n in range(1, 7) if n % 3 == 0}), 6)
    ),
    # Regla multiplicativa con independientes.
    "se anota su color y se devuelve a la caja": str(Fraction(6, 10) ** 2),
    "dado de 6 caras dos veces seguidas": str(Fraction(1, 6) ** 2),
    "3% de las piezas sale defectuosa": str(round(0.03**2, 4)).replace(".", ","),
    "independientes cumplen P(A) = 0,7": str(round(0.7 * 0.6, 2)).replace(".", ","),
    # Sin reposición: el segundo factor se calcula sobre lo que queda.
    "5 bolitas blancas y 7 negras": str(Fraction(5 - 1, 5 + 7 - 1)),
    "20 estudiantes, 12 practican": str(Fraction(12, 20) * Fraction(11, 19)),
    "13 corazones, se extraen dos cartas": str(Fraction(13, 52) * Fraction(12, 51)),
    "10 productos y 3 de ellos están defectuosos": str(Fraction(7, 10) * Fraction(6, 9)),
    "3 bolitas rojas y 3 azules": str(2 * Fraction(3, 6) * Fraction(2, 5)),
    # "Al menos uno" por complemento.
    "4 bolitas rojas y 6 azules. Se sacan dos": str(1 - Fraction(6, 10) * Fraction(5, 9)),
    "cuatro monedas equilibradas": str(1 - Fraction(1, 2) ** 4),
    "ganar una partida es 0,2": str(round((1 - 0.2) ** 3, 3)).replace(".", ","),
    # Tabla de doble entrada y probabilidad condicional: cambia el universo.
    "60 son mujeres y de ellas 40 usan lentes": str(Fraction(40, 100)),
    "200 personas encuestadas, 120 son hombres": str(Fraction(30, 80 + 30)),
    # Probabilidad total: ponderar cada grupo por su tamaño.
    "40% de los estudiantes son de primer año": str(round(0.4 * 0.25 + 0.6 * 0.10, 2)).replace(".", ","),
    # --- álgebra y funciones: segunda tanda ---
    # Reducción, productos notables y factorización.
    "reducir 9x − 4x + x": f"{9 - 4 + 1}x",
    "patio cuadrado de x metros de lado se amplía agregando 6 metros": f"x² + {2 * 6}x + {6**2}",
    "resultado de (x − 7)(x + 7)": f"x² − {7**2}",
    "plancha cuadrada de lado x centímetros tiene un hueco cuadrado de 9": f"(x + {round(81**0.5)})(x − {round(81**0.5)})",
    "costo de producir x artículos en un taller está dado por 8x² + 12x": f"4x(2x + {12 // 4})",
    "reducir 5(2x − 1) − 3(x + 2)": f"{5 * 2 - 3}x − {5 * 1 + 3 * 2}",
    "plancha cuadrada mide (2x − 5) centímetros de lado": f"{2**2}x² − {2 * 2 * 5}x + {5**2}",
    "huerto rectangular está dada por x² + 10x + 21": "x + 7" if 3 * 7 == 21 and 3 + 7 == 10 else "?",
    "simplificar (x² − 49)/(x + 7)": f"x − {round(49**0.5)}",
    "área sobrante de una lámina está dada por 5x² − 45": f"5(x + {round((45 // 5) ** 0.5)})(x − {round((45 // 5) ** 0.5)})",
    "simplificar (x² + 6x + 9)/(x + 3)": f"x + {round(9**0.5)}",
    # Identidades: (a+b)² y (a−b)² despejadas.
    "Dos tablones miden juntos 12 metros": str(12**2 - 2 * 35),
    "x − y = 4 y x · y = 5": str(4**2 + 2 * 5),
    "lados que miden (2x + 3) y (x − 1)": f"{2 * (2 + 1)}x + {2 * (3 - 1)}",
    # Ecuaciones lineales.
    "ecuación 4x + 7 = 23": f"x = {(23 - 7) // 4}",
    "ecuación 3x − 5 = 16": f"x = {(16 + 5) // 3}",
    "ecuación x/4 = 6": f"x = {6 * 4}",
    "jugador parte con 9 puntos y juega 2 rondas": f"x = {(3 - 9) // 2}",
    "ecuación 5x − 3 = 2x + 12": f"x = {(12 + 3) // (5 - 2)}",
    "(x + 1)/4 = (x − 5)/2": f"x = {(4 * 5 + 2 * 1) // (4 - 2)}",
    "número aumentado en 7 es igual al triple": str((7 + 5) // (3 - 1)),
    "$500 de bajada de bandera": f"{(5000 - 500) // 300} km",
    # Inecuaciones, incluido el caso en que el signo se invierte.
    "inecuación x + 8 > 12": f"x > {12 - 8}",
    "inecuación 3x + 4 ≤ 19": f"x ≤ {(19 - 4) // 3}",
    "inecuación −2x + 6 > 0": f"x < {6 // 2}",
    "inecuación −3x + 5 ≥ 14": f"x ≤ {(5 - 14) // 3}",
    "enteros positivos cumplen la inecuación 2x − 3 < 11": str(
        len([x for x in range(1, 50) if 2 * x - 3 < 11])
    ),
    "plan de internet A cuesta $8.000": f"Desde {(12_000 - 8_000) // (200 - 100) + 1} GB",
    # Sistemas 2x2.
    "x + y = 10 y x − y = 4": str((10 + 4) // 2),
    "x + y = 15 e y = 4x": str(15 // (1 + 4)),
    "2x + y = 11 e y = 3": str((11 - 3) // 2),
    "x = 5 y x + y = 9": str(9 - 5),
    "x + y = 7 y x − y = 1": str((7 - 1) // 2),
    "3x + 2y = 16 y x − 2y = 0": str(16 // (3 + 1)),
    "2x + 3y = 15 y x = y": str(15 // (2 + 3)),
    "suma de dos números es 30 y su diferencia es 8": str((30 + 8) // 2),
    "x + 2y = 8 y 3x − y = 3": str((3 * 8 - 3) // (3 * 2 + 1)),
    "4x + 3y = 18 y 2x − y = 4": f"x = {(18 + 3 * 4) // (4 + 3 * 2)} e y = {2 * ((18 + 3 * 4) // (4 + 3 * 2)) - 4}",
    "Cinco lápices y tres cuadernos cuestan $4.100": "$" + f"{1500 - 2 * 400:,}".replace(",", "."),
    "25 animales y 82 patas": str((82 - 2 * 25) // 2),
    "suma de dos números es 25 y el mayor es 4 unidades": str(2 * ((25 - 4) // 3) + 4),
    # Ecuaciones cuadráticas.
    "ecuación x² = 121": f"x = {round(121**0.5)} y x = -{round(121**0.5)}",
    "ecuación x² − 100 = 0": f"x = {round(100**0.5)} y x = -{round(100**0.5)}",
    "ecuación (x − 3)(x + 5) = 0": f"x = {3} y x = -{5}",
    "ecuación x² − 5x = 0": f"x = 0 y x = {5}",
    "ecuación x² + 2x + 1 = 0": f"x = -{2 // 2}",
    "ecuación x² − 7x + 12 = 0": "x = 3 y x = 4" if 3 * 4 == 12 and 3 + 4 == 7 else "?",
    "ecuación x² + x − 6 = 0": "x = 2 y x = -3" if 2 * -3 == -6 and 2 + -3 == -1 else "?",
    "ecuación 2x² − 8 = 0": f"x = {round((8 // 2) ** 0.5)} y x = -{round((8 // 2) ** 0.5)}",
    "ecuación x² − 8x + 16 = 0": f"x = {8 // 2}",
    "suma de las soluciones de la ecuación x² − 13x + 42 = 0": str(6 + 7),
    "producto de las soluciones de la ecuación 3x² + 7x − 6 = 0": str(Fraction(-6, 3)),
    "área de 54 m² y su largo mide 3 m más": f"{6} m y {6 + 3} m",
    "x² + kx + 9 = 0 tenga una única solución": str(round((4 * 1 * 9) ** 0.5)),
    # Funciones: evaluación, cortes con los ejes, pendiente y vértice.
    "f(x) = 3x − 2, ¿cuál es el valor de f(4)": str(3 * 4 - 2),
    "f(x) = x² + 1, ¿cuál es el valor de f(3)": str(3**2 + 1),
    "corta al eje Y la recta de ecuación y = 2x − 7": f"(0, -{7})",
    "pendiente de la recta de ecuación y = −5x + 3": str(-5),
    "f(x) = 2x, ¿qué valores toma": f"{2 * 0}, {2 * 1}, {2 * 2} y {2 * 3}",
    "cero de la función f(x) = 4x − 12": f"x = {12 // 4}",
    "corta al eje X la recta de ecuación y = 3x − 9": f"({9 // 3}, 0)",
    "pasa por el punto (0, 4) y tiene pendiente 2": f"y = {2}x + {4}",
    "ceros de la función f(x) = x² − 7x": f"x = 0 y x = {7}",
    "pasa por los puntos (1, 5) y (3, 11)": str((11 - 5) // (3 - 1)),
    # Vértice: x = -b/(2a), y después se evalúa.
    "vértice de la parábola de ecuación y = x² − 8x + 7": f"({8 // 2}, {(8 // 2) ** 2 - 8 * (8 // 2) + 7})",
    "vértice de la parábola de ecuación y = 2x² + 8x + 5": f"({-8 // (2 * 2)}, {2 * (-2) ** 2 + 8 * -2 + 5})",
    # --- semejanza y proporcionalidad de figuras (nodo nuevo) ---
    # De plano a realidad se MULTIPLICA por la escala.
    "escala 1 : 200, un muro aparece dibujado con 4 cm": f"{4 * 200 // 100} m",
    "1 : 50, una ventana aparece con 6 cm": f"{6 * 50 // 100} m",
    "1 : 1.000, un terreno aparece con 12 cm de frente": f"{12 * 1_000 // 100} m",
    "1 : 80, un pasillo aparece con 5 cm": f"{5 * 80 // 100} m",
    "1 : 150, dos puntos aparecen separados por 8 cm": f"{8 * 150 // 100} m",
    "1 : 500.000, dos ciudades aparecen separadas por 3 cm": f"{3 * 500_000 // 100_000} km",
    "1 : 400.000, una ruta aparece con 3,5 cm": f"{round(3.5 * 400_000 / 100_000)} km",
    "1 cm representa 2 km": f"{7 * 2} km",
    # De realidad a plano o maqueta se DIVIDE.
    "maqueta está hecha a escala 1 : 20": f"{40 // 20} m",
    "sala mide 7 m de largo en la realidad": f"{7 * 100 // 100} cm",
    "pieza mide 75 cm en la realidad": f"{75 // 25} cm",
    "pared mide 6 m de largo": f"{6 * 100 // 150} cm",
    "auto mide 4,8 m de largo": f"{round(4.8 * 100) // 40} cm",
    "edificio mide 30 m de alto": str(30 / 25).replace(".", ",") + " m",
    "avión mide 64 m de largo": f"{64 // 32} m",
    "1 : 250.000, ¿con cuántos centímetros": f"{60 * 100_000 // 250_000} cm",
    # Deducir la escala a partir de dos medidas.
    "5 cm representan 10 m": f"1 : {10 * 100 // 5}",
    "terreno de 40 m de frente": f"1 : {40 * 100 // 20}",
    # Razón de semejanza aplicada a lados y perímetros (misma razón).
    "razón de semejanza 1 : 3. Si un lado del triángulo menor mide 5 cm": f"{5 * 3} cm",
    "razón de semejanza 2 : 3. Si el perímetro del menor es 24 cm": f"{24 * 3 // 2} cm",
    "razón de semejanza 3 : 4. Si un lado de la primera mide 12 cm": f"{12 * 4 // 3} cm",
    "razón de semejanza 5 : 2. Si un lado de la figura mayor mide 35 cm": f"{35 * 2 // 5} cm",
    "razón de semejanza 3 : 5. Si el perímetro del mayor es 45 cm": f"{45 * 3 // 5} cm",
    "razón 4 : 7. Si un lado del menor mide 12 cm": f"{12 * 7 // 4} cm",
    "perímetros de 36 cm y 48 cm": f"{9 * 48 // 36} cm",
    "razón 3 : 5. Si la altura del menor mide 12 cm": f"{12 * 5 // 3} cm",
    "un lado de 4 cm le corresponde uno de 6 cm": str(round(9 * 6 / 4, 1)).replace(".", ",") + " cm",
    "primero mide 4 cm por 6 cm y el segundo tiene 10 cm de ancho": f"{10 * 6 // 4} cm",
    "lados de 8 cm, 12 cm y 16 cm": f"{12 * 3 // 2} cm y {16 * 3 // 2} cm",
    "lados de 9 cm, 12 cm y 15 cm": f"{12 * 2 // 3} cm y {15 * 2 // 3} cm",
    # Razones deducidas desde medidas.
    "cuadrado tiene 4 cm de lado y otro tiene 12 cm": f"1 : {12 // 4}",
    "lados correspondientes de 5 cm y 20 cm": f"1 : {20 // 5}",
    "círculos tienen radios de 2 cm y 6 cm": f"1 : {6 // 2}",
    "perímetros de 20 cm y 50 cm": f"{20 // 10} : {50 // 10}",
    # Ampliaciones y reducciones: las dos dimensiones por el mismo factor.
    "fotografía de 8 cm de ancho se amplía al doble": f"{8 * 2} cm",
    "rectángulo de 3 cm por 5 cm se amplía al triple": f"{3 * 3} cm por {5 * 3} cm",
    "fotografía de 10 cm por 15 cm se reduce a la mitad": f"{10 // 2} cm por "
    + str(15 / 2).replace(".", ",")
    + " cm",
    "6 cm de ancho por 9 cm de alto y se amplía": str(round(9 * 15 / 6, 1)).replace(".", ",") + " cm",
    "fotografía de 12 cm por 18 cm se amplía 1,5 veces": f"{round(2 * (12 * 1.5 + 18 * 1.5))} cm",
    # Sombras y espejos: triángulos semejantes en el mundo real.
    "poste de 6 m proyecta una sombra de 8 m": str(round(6 * 2 / 8, 1)).replace(".", ",") + " m",
    "bastón de 1 m proyecta una sombra de 0,8 m": f"{round(12 / 0.8)} m",
    "poste de 5 m proyecta una sombra de 4 m": f"{28 * 5 // 4} m",
    "espejo en el suelo": f"{round(1.6 * 15 / 2)} m",
    # Teorema de Tales.
    "segmentos de 3 cm y 4 cm; en la segunda": f"{6 * 4 // 3} cm",
    "segmentos de 8 cm y 12 cm; sobre la otra": str(round(5 * 12 / 8, 1)).replace(".", ",") + " cm",
    "AD mide 4 cm, DB mide 6 cm y AE mide 6 cm": f"{6 * 6 // 4} cm",
    "segmentos de 6 cm y 4 cm. Si el tercer lado mide 15 cm": f"{15 * 6 // 10} cm y {15 * 4 // 10} cm",
    "le corresponde uno de x cm": f"{round((3 * 12) ** 0.5)} cm",
    # Áreas: la razón va AL CUADRADO.
    "razón de semejanza 2 : 5. Si el área de la menor es 16 cm²": f"{16 * 5**2 // 2**2} cm²",
    "razón de semejanza 1 : 4. Si el área de la menor es 7 cm²": f"{7 * 4**2} cm²",
    "razón 2 : 3. Si el área del menor es 24 cm²": f"{24 * 3**2 // 2**2} cm²",
    "razón 2 : 5. Si el área del menor es 60 cm²": f"{60 * 5**2 // 2**2} cm²",
    "razón 9 : 16": f"{round(9**0.5)} : {round(16**0.5)}",
    "razón 25 : 49": f"{round(25**0.5)} : {round(49**0.5)}",
    "1 : 200, una bodega ocupa 25 cm²": f"{25 * 200**2 // 10_000} m²",
    "1 : 2.000, un terreno ocupa 4 cm²": f"{4 * 2_000**2 // 10_000:,}".replace(",", ".") + " m²",
    "superficie real de 18 m²": f"{18 * 10_000 // 60**2} cm²",
    "1 : 50.000, un lago ocupa 3 cm²": str(3 * 50_000**2 / 10_000 / 1_000_000).replace(".", ",") + " km²",
    # Volúmenes: la razón va AL CUBO.
    "razón de semejanza 1 : 2. Si el volumen del menor es 5 cm³": f"{5 * 2**3} cm³",
    "maqueta está hecha a escala 1 : 50": "1 : " + f"{50**3:,}".replace(",", "."),
    "cubos son semejantes con razón de semejanza 2 : 3": f"{16 * 3**3 // 2**3} cm³",
    "razón 8 : 27": f"{round(8 ** (1 / 3))} : {round(27 ** (1 / 3))}",
    "piscina mide 25 m de largo, 10 m de ancho y 2 m de profundidad": f"{25 * 10 * 2} cm³",
    # --- reposición de geo_plana ---
    "pista de atletismo": f"{2880 // (2 * (84 + 60))} vueltas",
    "jardín rectangular mide 20 m por 12 m": f"{20 * 12 - (20 - 2 * 2) * (12 - 2 * 2)} m²",
    "24 cm de base y 10 cm de altura": f"{(24 - 9) * 10 // 2} cm²",
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
    "patios cuadrados miden 169 y 36 metros cuadrados": str(int(sqrt(169) + sqrt(36))),
    "(5⁴ · 5²) ÷ 5³": str(5**4 * 5**2 // 5**3),
    "3⁻³": str(Fraction(1, 3**3)),
    "cultivo se triplica cada hora": str(4 if 3**4 == 81 else None),
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
    "kiosco recibe 7 cajas de bebidas": f"{7 - 3 + 2}x",
    "feria vende 6 cajones de manzanas y 4 de naranjas": f"{6 - 2}m − {9 - 4}n",
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
    "arrienda 5 camionetas a un costo de (2a − 3) miles": f"{5 * 2 - 3}a − {5 * 3 - 3 * 4}",
    "2x² − 18": f"2(x + {int(sqrt(9))})(x − {int(sqrt(9))})",
    "a + b = 7 y ab = 12": str(7**2 - 2 * 12),
    "a − b = 5 y ab = 6": str(5**2 + 2 * 6),
    "(x² + 5x + 6)/(x + 2)": f"x + {6 // 2}",
    "(x² − 4)/(x² + 4x + 4)": f"(x − {2})/(x + {2})",
    "taller tiene 8 planchas de metal": f"{8 - 1 + 3}y",
    "reducir 3a + 7b − a − 2b": f"{3 - 1}a + {7 - 2}b",
    "(x + 1)(x + 9)": f"x² + {1 + 9}x + {1 * 9}",
    "(2x + 3)²": f"{2**2}x² + {2 * 2 * 3}x + {3**2}",
    "terreno cuadrado de lado x metros se le quita un cuadrado de 10": f"(x + {int(sqrt(100))})(x − {int(sqrt(100))})",
    "factorización de 5x² − 15x": f"5x(x − {15 // 5})",
    "doble de un número aumentado en 7": f"2n + {7}",
    "reducir 4(x − 2) + 3x": f"{4 + 3}x − {4 * 2}",
    "rectángulo tiene área x² + 11x + 30": "(x + 5) y (x + 6)" if 5 * 6 == 30 and 5 + 6 == 11 else "?",
    "factorización de x² − 8x + 15": "(x − 3)(x − 5)" if 3 * 5 == 15 and 3 + 5 == 8 else "?",
    "factorización de x² + 2x − 24": "(x + 6)(x − 4)" if 6 * -4 == -24 and 6 - 4 == 2 else "?",
    "(4x + 12) litros de pintura entre (x + 3) locales": str(12 // 3),
    "2x² − 5x + 4": str(2 * 3**2 - 5 * 3 + 4),
    "3 estudiantes aportan (2m + 5) pesos cada uno": f"{3 * 2 - 2}m + {3 * 5 + 2}",
    "(3x − 2)(3x + 2)": f"{3**2}x² − {2**2}",
    "largo (x + 5) y ancho (x − 2)": f"{2 * 2}x + {2 * (5 - 2)}",
    "lados de un rectángulo suman 10 centímetros y su área es 21": str(10**2 - 2 * 21),
    "terreno rectangular tiene área x² − 7x + 12": f"x − {12 // 3}",
    "factorización completa de 3x² − 27": f"3(x + {int(sqrt(9))})(x − {int(sqrt(9))})",
    "(x² + 6x + 9)/(x² − 9)": f"(x + {3})/(x − {3})",
    # --- ecuaciones e inecuaciones lineales ---
    "vendedor recibe 5 cajas de igual cantidad": str((12 + 8) // 5),
    "x/4 + 3 = 8": str((8 - 3) * 4),
    "cobra 2 mil pesos por hora más 9 mil fijos": str(9 + 1),
    "5 puntos acumulados en una tarjeta": f"x > {12 - 5}",
    "ascensor soporta como máximo 20 unidades": f"x ≤ {20 // 4}",
    "7 − x = 2": str(7 - 2),
    "primero tiene 6 álbumes iguales": str(14 // (6 - 4)),
    "compra 4 lotes que traen (x + 3) equipos": str((20 - 4 * 3) // (4 - 2)),
    "5(x − 1) = 3(x + 3)": str((3 * 3 + 5 * 1) // (5 - 3)),
    "plan A cobra 5 mil pesos por hora menos un descuento": f"x ≥ {(9 + 3) // (5 - 2)}",
    "la mitad para un hermano y un tercio para otro": str(int(5 / (Fraction(1, 2) + Fraction(1, 3)))),
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
    "reparte a cada curso la mitad de (x + 5) cajas": f"x ≥ {5 + 2}",
    "número más su tercera parte": str(int(32 / (1 + Fraction(1, 3)))),
    "despacha 5 pallets con (x − 2) cajas": str((7 + 5 * 2 + 3) // (5 - 3)),
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
    "baldosa cuadrada tiene un área de 36": f"{int(sqrt(36))} cm",
    "huerto cuadrado ocupa 81 metros cuadrados": f"{int(sqrt(81))} m",
    "x² − 6x = 0": f"x = 0 y x = {6}",
    "x² + 5x + 6 = 0": f"x = −{2} y x = −{3}" if 2 * 3 == 6 and 2 + 3 == 5 else "?",
    "x² − 9x + 20 = 0": f"x = {4} y x = {5}" if 4 * 5 == 20 and 4 + 5 == 9 else "?",
    "x² + 3x − 18 = 0": f"x = {3} y x = −{6}" if 3 * -6 == -18 and 3 - 6 == -3 else "?",
    "lado que mide 2 metros menos que el otro y su área es 8": ("4 m" if 4 * 2 == 8 and 4 - 2 == 2 else "?"),
    "área total de 3 cuadrados iguales es 12": f"{int(sqrt(12 // 3))} cm",
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
    "las edades de dos hermanos": str(2 + 5) if 2 * 5 == 10 and 2 + 5 == 7 else "?",
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
    "f(x) = 4x + b cumple que f(2) = 11": str(11 - 4 * 2),
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
    # El fragmento lleva los números porque hay más de una pregunta que empieza
    # con "Ordena de menor a mayor las fracciones".
    "Ordena de menor a mayor las fracciones 2/3": ", ".join(
        str(f) for f in sorted([Fraction(2, 3), Fraction(3, 5), Fraction(7, 10)])
    ),
    "(3/4 − 1/6) ÷ (1/2 + 1/3)": str(
        (Fraction(3, 4) - Fraction(1, 6)) / (Fraction(1, 2) + Fraction(1, 3))
    ),
    "3/4 de kilo de café en 6 bolsas": str(Fraction(3, 4) / 6),
    "cubo tiene 4 centímetros de arista": str(4**3),
    "√100 + √9": str(int(sqrt(100) + sqrt(9))),
    "2⁵ · 2²": str(2**5 * 2**2),
    "cultivo se cuadruplica cada día": str((2**2) ** 4),
    "10⁻²": str(Fraction(1, 10**2)),
    "√64 · √4": str(int(sqrt(64) * sqrt(4))),
    "(4³ · 4²) ÷ 4⁴": str(4**3 * 4**2 // 4**4),
    "patio cuadrado tiene una superficie de 72": "6" if isclose(sqrt(72), 6 * sqrt(2)) else "?",
    "(5²)³ ÷ 5⁴": str((5**2) ** 3 // 5**4),
    "3⁰ + 2⁻¹": str(1 + Fraction(1, 2)),
    "√98 − √50": "2" if isclose(sqrt(98) - sqrt(50), 2 * sqrt(2)) else "?",
    "plaza cuadrada tiene un área de 121 m²": f"{int(sqrt(121))} m",
    "imagen se reduce 3 veces a la mitad": str(2 ** (-3 + 5)),
    "5ˣ = 625": str(4 if 5**4 == 625 else None),
    "(3⁻² · 3⁵) ÷ 3²": str(3 ** (-2 + 5 - 2)),
    "√(5² + 12²)": str(int(sqrt(5**2 + 12**2))),
    "2³ + 3²": str(2**3 + 3**2),
    "misma superficie que un rectángulo de 16 por 25": str(int(sqrt(16 * 25))),
    "(7²)⁰": str(7**0),
    "depósito de agua duplica su contenido cada hora": str(5 if 2 ** (5 - 1) == 16 else None),
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
    "rectángulo que mide 16 cm por 30 cm": f"{int(sqrt(16**2 + 30**2))} cm",
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
    "paralelepípedo de 9 cm de largo, 7 cm de ancho": f"{9 * 7 * 4} cm³",
    "caja cúbica tiene un área total de 216 cm²": f"{round((216 / 6) ** 0.5)} cm",
    "paralelepípedo mide 6 cm, 4 cm y 3 cm": f"{2 * (6 * 4 + 6 * 3 + 4 * 3)} cm²",
    "estanque cilíndrico tiene 2 m de radio": f"{3.14 * 2**2 * 3:.2f} m³".replace(".", ","),
    "arista de un cubo se triplica": str(3**3),
    "cubo tiene un volumen de 64 cm³": f"{round(64 ** (1 / 3))} cm",
    "cilindro tiene un volumen de 502,4 cm³": f"{round(502.4 / (3.14 * 4**2))} cm",
    "volumen de 60 cm³ y dos de sus dimensiones": f"{60 // (5 * 3)} cm",
    "cubos de 5 cm de arista caben": f"{20 * 15 * 10 // 5**3} cubos",
    "área total de un cilindro de radio 3 cm y altura 7 cm": (
        f"{2 * 3.14 * 3**2 + 2 * 3.14 * 3 * 7:.1f} cm²".replace(".", ",")
    ),
    "estanque cúbico de 30 cm de arista": f"{30**3 // 1000} litros",
    # Cuerpos con el mismo volumen: el dato que los conecta.
    "cubo de 6 cm de arista y un paralelepípedo": f"{6**3 // (9 * 8)} cm",
    "arista de un cubo se reduce a la mitad": f"Por 1/{2**3}",
    "duplica la altura de un cilindro": str(2),
    # ================= LOTE 8 — eje PROBABILIDAD Y ESTADÍSTICA =================
    "media de los datos 5, 10, 15 y 20": f"{(5 + 10 + 15 + 20) / 4:.1f}".replace(".", ","),
    "mediana de los datos 6, 14, 8, 20 y 12": str(sorted([6, 14, 8, 20, 12])[2]),
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
    "9 camisas y 4 corbatas": str(9 * 4),
    "letras de la palabra SOL": str(factorial(3)),
    "comité de 3 personas a partir de un grupo de 5": str(comb(5, 3)),
    "elegir 2 personas de un grupo de 8": str(comb(8, 2)),
    "carrera con 5 corredores": str(5 * 4 * 3),
    "2 cifras distintas se pueden formar usando los dígitos 1, 2, 3 y 4": str(4 * 3),
    "patente se forma con 3 letras": f"{26**3:,}".replace(",", "."),
    "3 entradas, 4 platos de fondo y 2 postres": str(3 * 4 * 2),
    "subconjuntos de 2 elementos tiene un conjunto de 11": str(comb(11, 2)),
    "letras de la palabra PERRO": str(factorial(5) // factorial(2)),
    "comité de 4 personas de un grupo de 7": str(comb(7, 4)),
    "plantel de 10 jugadores": str(comb(10, 5)),
    "4 cifras distintas se pueden formar con los dígitos del 0 al 9": f"{9 * 9 * 8 * 7:,}".replace(",", "."),
    "claves distintas de 4 dígitos": f"{10**4:,}".replace(",", "."),
    "reunión de 8 personas": str(comb(8, 2)),
    "ordenar 7 personas en una fila": f"{factorial(7):,}".replace(",", "."),
    "6 hombres y 4 mujeres": str(comb(6, 2) * comb(4, 2)),
}


_SUPERINDICES = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def _numeros_del_stem(stem: str) -> tuple[str, ...]:
    """Los números que aparecen en un enunciado, incluidos los exponentes.

    Los exponentes se escriben en superíndice (2³, x²) y `\\d` no los reconoce.
    Sin traducirlos, "2³ · 2⁴" y "2⁵ · 2²" tienen la misma firma numérica y el
    detector de duplicados los daría por repetidos sin serlo.
    """
    return tuple(sorted(re.findall(r"\d+(?:[.,]\d+)?", stem.translate(_SUPERINDICES))))


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

    # Dos preguntas del mismo nodo con los mismos números Y la misma respuesta
    # correcta son la misma pregunta reformulada, aunque el enunciado no calce
    # letra por letra. Al estudiante le tocan repetidas dentro de un mismo
    # ensayo, que es justo lo que no puede pasar. Antes esto era solo un aviso
    # y por eso el banco acumuló pares como "¿cuánto mide LA hipotenusa?" y
    # "¿cuánto mide SU hipotenusa?" con los mismos catetos.
    por_firma: dict[tuple[str, tuple[str, ...], str], list[str]] = {}
    for q in QUESTIONS:
        numeros = _numeros_del_stem(q["stem"])
        if not numeros:
            continue
        correcta = next(a["text"] for a in q["alternatives"] if a["is_correct"])
        por_firma.setdefault((q["skill_node"], numeros, correcta), []).append(q["stem"])
    for (nodo, numeros, correcta), stems in por_firma.items():
        if len(stems) > 1:
            detalle = "\n".join(f"        · {st[:76]}" for st in stems)
            fallas.append(
                f"{nodo}: {len(stems)} preguntas con los mismos números {numeros} y la misma "
                f"respuesta '{correcta}'; son la misma pregunta reformulada:\n{detalle}"
            )

    # Dos alternativas con el MISMO VALOR dejan la pregunta con dos respuestas
    # correctas. Comparar los textos no basta: "3/4" y "9/12" son cadenas
    # distintas y el mismo número, y el alumno que resuelve bien pero no
    # simplifica queda malo. Solo se comparan alternativas que sean un número
    # limpio: "x < −3" y "x > −3" comparten el 3 sin ser lo mismo.
    for q in todas:
        puros: dict[Fraction, str] = {}
        for a in q["alternatives"]:
            texto = _norm(a["text"])
            if not re.fullmatch(r"-?\d+(?:[.,]\d+)?(?:\s*/\s*-?\d+)?", texto):
                continue
            valores = _valores_del_texto(texto)
            if len(valores) != 1:
                continue
            valor = next(iter(valores))
            if valor in puros:
                fallas.append(
                    f"dos alternativas valen lo mismo ('{puros[valor]}' y "
                    f"'{a['text']}'): {q['stem'][:60]}"
                )
            puros[valor] = a["text"]

    # Una plantilla es un enunciado con los números cambiados. Si la tarea es la
    # misma, la dificultad tiene que ser la misma: el ensayo se arma con esa
    # etiqueta. Cuando los números SÍ cambian el procedimiento, la excepción se
    # declara arriba con su motivo, para que sea una decisión y no un descuido.
    por_plantilla: dict[tuple[str, str], list[dict]] = {}
    for q in QUESTIONS:
        plantilla = re.sub(r"\d+", "N", q["stem"])
        por_plantilla.setdefault((q["skill_node"], plantilla), []).append(q)
    for (nodo, plantilla), grupo in por_plantilla.items():
        etiquetas = {q["difficulty"] for q in grupo}
        if len(etiquetas) < 2:
            continue
        if any(
            frag in q["stem"] for q in grupo for frag in EXCEPCIONES_DIFICULTAD
        ):
            continue
        detalle = "\n".join(
            f"        · [{q['difficulty']}] {q['stem'][:70]}" for q in grupo
        )
        fallas.append(
            f"{nodo}: misma plantilla con dificultades {sorted(etiquetas)}; "
            f"si la tarea es la misma la etiqueta debe serlo:\n{detalle}"
        )

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
