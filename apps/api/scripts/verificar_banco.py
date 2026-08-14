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
