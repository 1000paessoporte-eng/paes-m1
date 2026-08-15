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
}


def _norm(t: str) -> str:
    """Normaliza para comparar: el banco usa el signo menos U+2212, no el guion."""
    return t.replace("\u2212", "-").replace("\u00a0", " ").strip()


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
