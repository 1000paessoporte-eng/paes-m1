"""Revision del banco que `verificar_banco.py` no hace.

`verificar_banco.py` es el porton: falla y bloquea. Esto es distinto —informa y
no bloquea— porque lo que busca son indicios que necesitan un ojo humano
despues, no defectos que se puedan afirmar por si solos.

Cuatro revisiones, en orden de lo que han encontrado en la practica:

1. DUPLICADOS POR PARAFRASIS. La misma pregunta redactada de dos maneras
   dentro de un nodo. Importa porque los ensayos sacan preguntas al azar del
   nodo: las dos pueden caerle al mismo alumno en la misma sesion. Un par con
   enunciados parecidos y respuestas DISTINTAS es una variante legitima del
   mismo molde, que es lo que un banco debe tener; el problema aparece cuando
   tambien coincide la respuesta.

2. COBERTURA DE ARITMETICA. De las preguntas cuya respuesta es un numero,
   cuantas tienen una entrada en COMPROBACIONES que la recalcule. Las que no,
   estan respaldadas solo por el ojo de quien las escribio.

3. ESTRUCTURA. Alternativas repetidas, justificaciones vacias o repetidas,
   preguntas sin una unica correcta, explicaciones que nombran letras (seed.py
   mezcla el orden), y la respuesta servida dentro del enunciado.

4. APOYO EN EL TEXTO. Para las preguntas que dicen "segun el texto", si algun
   distractor reutiliza el vocabulario del texto mucho mas que la correcta.
   Suele ser buena senal —el distractor es una trampa lexica y la correcta
   parafrasea— pero ordena por donde mirar si algo se sospecha.

Uso:
    PYTHONIOENCODING=utf-8 python -m uv run python scripts/revisar_banco.py
    ... --solo duplicados|cobertura|estructura|texto   para una sola
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

from paes_api.seed_data import (
    PASSAGES,
    PASSAGES_HISTORIA,
    QUESTIONS,
    QUESTIONS_CIENCIAS,
    QUESTIONS_HISTORIA,
    QUESTIONS_LECTORA,
)

BANCOS = {
    "matematica": QUESTIONS,
    "lectora": QUESTIONS_LECTORA,
    "ciencias": QUESTIONS_CIENCIAS,
    "historia": QUESTIONS_HISTORIA,
}
TEXTOS = {p["key"]: p for p in PASSAGES + PASSAGES_HISTORIA}

#: Palabras sin contenido, que ensucian cualquier medida de parecido entre dos
#: enunciados. Se escriben como texto y se parten: la lista literal equivalente
#: ocupa una sola linea de 1.400 caracteres y no hay como leerla.
VACIAS = frozenset("""a al algo alguna algunas alguno algunos ante antes aquel
aquella aquello asi aun aunque cada como con contra cual cuales cuando cuanta
cuantas cuanto cuantos de del desde donde dos el ella ellas ello ellos en entre
era eran es esa esas ese eso esos esta estan estas este esto estos fue fueron ha
hace hacia han hasta hay la las le les lo los mas me mi mientras mucho muy nada
ni no nos o otra otras otro otros para pero poco por porque que quien quienes se
sea segun ser si sin sobre solo son su sus tal tambien tan tanto te tiene tienen
toda todas todo todos tras un una unas uno unos y ya siguientes siguiente
afirmaciones afirmacion expresiones expresion representa correcta correctamente
texto""".split())  # noqa: SIM905


def _sin_tildes(s: str) -> str:
    t = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def terminos(s: str, largo_min: int = 3) -> set[str]:
    """Palabras de contenido. Los numeros se conservan aunque sean cortos:
    en matematica son todo el contenido del enunciado."""
    palabras = re.sub(r"[^a-z0-9ñ ]+", " ", _sin_tildes(s)).split()
    return {p for p in palabras
            if p not in VACIAS and (p.isdigit() or len(p) > largo_min)}


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


# --------------------------------------------------------------------------
# 1. duplicados por parafrasis
# --------------------------------------------------------------------------
def revisar_duplicados(umbral_stem: float, umbral_resp: float) -> list[str]:
    por_nodo: dict[tuple[str, str], list] = defaultdict(list)
    for prueba, banco in BANCOS.items():
        for q in banco:
            por_nodo[(prueba, q["skill_node"])].append(q)

    hallazgos = []
    for (prueba, nodo), qs in por_nodo.items():
        cache = []
        for q in qs:
            c = next(a["text"] for a in q["alternatives"] if a["is_correct"])
            cache.append((q, terminos(q["stem"]), terminos(c), c))
        for (q1, t1, r1, c1), (q2, t2, r2, c2) in combinations(cache, 2):
            if min(len(t1), len(t2)) < 6:
                continue
            se = jaccard(t1, t2)
            if se < umbral_stem:
                continue
            sr = 1.0 if c1.strip() == c2.strip() else jaccard(r1, r2)
            if sr < umbral_resp:
                continue
            hallazgos.append(
                f"[{prueba}/{nodo}] enunciado {se:.2f} · respuesta {sr:.2f}\n"
                f"      A ({q1['difficulty']}) {re.sub(r'\\s+', ' ', q1['stem'])[:105]}\n"
                f"      B ({q2['difficulty']}) {re.sub(r'\\s+', ' ', q2['stem'])[:105]}\n"
                f"      -> {c1[:70]}"
            )
    return hallazgos


# --------------------------------------------------------------------------
# 2. cobertura de aritmetica
# --------------------------------------------------------------------------
NUMERICA = re.compile(r"^[^a-zA-Z]*-?\d[\d.,]*\s*[a-zA-Z%²³/]*\s*$")


def claves_de_comprobaciones() -> list[str]:
    fuente = (RAIZ / "scripts" / "verificar_banco.py").read_text(encoding="utf-8")
    claves = []
    for nodo in ast.walk(ast.parse(fuente)):
        if (isinstance(nodo, ast.AnnAssign)
                and isinstance(nodo.target, ast.Name)
                and nodo.target.id.startswith("COMPROBACIONES")
                and isinstance(nodo.value, ast.Dict)):
            claves += [k.value for k in nodo.value.keys
                       if isinstance(k, ast.Constant) and isinstance(k.value, str)]
    return [_sin_tildes(k) for k in claves]


def revisar_cobertura() -> tuple[list[str], list[str]]:
    claves = claves_de_comprobaciones()
    resumen, faltantes = [], []
    for prueba, banco in BANCOS.items():
        n = c = 0
        for q in banco:
            correcta = next(a["text"] for a in q["alternatives"] if a["is_correct"])
            if not NUMERICA.match(correcta.replace("×", "").replace("¹⁰", "")):
                continue
            n += 1
            s = _sin_tildes(re.sub(r"\s+", " ", q["stem"]))
            if any(k in s for k in claves):
                c += 1
            else:
                faltantes.append(
                    f"[{prueba}/{q['skill_node']}] {re.sub(r'\\s+', ' ', q['stem'])[:95]}"
                )
        pct = f"{100 * c // n}%" if n else "-"
        resumen.append(f"{prueba:12s} {n:5d} numericas · {c:5d} recomprobadas ({pct})")
    return resumen, faltantes


# --------------------------------------------------------------------------
# 3. estructura
# --------------------------------------------------------------------------
def revisar_estructura() -> dict[str, list[str]]:
    fallas: dict[str, list[str]] = defaultdict(list)
    stems = Counter()
    for prueba, banco in BANCOS.items():
        for q in banco:
            etiqueta = (f"[{prueba}/{q['skill_node']}] "
                        f"{re.sub(r'\\s+', ' ', q['stem'])[:80]}")
            alts = q["alternatives"]
            correctas = [a for a in alts if a["is_correct"]]
            if len(correctas) != 1:
                fallas["sin una unica correcta"].append(etiqueta)
                continue
            otras = [a for a in alts if not a["is_correct"]]
            if len({" ".join(a["text"].split()) for a in alts}) != len(alts):
                fallas["alternativas repetidas"].append(etiqueta)
            just = [(a["justification"] or "").strip() for a in otras]
            if any(not j for j in just):
                fallas["distractor sin justificacion"].append(etiqueta)
            elif len(set(just)) != len(just):
                fallas["justificaciones repetidas"].append(etiqueta)
            if re.search(r"\b(alternativa|opci[oó]n) [A-E]\b", q.get("explanation", "")):
                fallas["la explicacion nombra una letra"].append(etiqueta)
            tc = _sin_tildes(correctas[0]["text"])
            if len(tc) > 25 and tc in _sin_tildes(q["stem"]):
                fallas["la respuesta esta en el enunciado"].append(etiqueta)
            clave = q.get("passage")
            if clave and clave not in TEXTOS:
                fallas["texto base inexistente"].append(f"{etiqueta} -> {clave}")
            stems[_sin_tildes(re.sub(r"\s+", " ", q["stem"]))] += 1
    for s, n in stems.items():
        if n > 1:
            fallas["enunciado duplicado literal"].append(f"x{n}: {s[:80]}")
    return fallas


# --------------------------------------------------------------------------
# 4. apoyo en el texto base
# --------------------------------------------------------------------------
PIDE_TEXTO = re.compile(
    r"seg[uú]n (el|la|los|las|est|ambas)|de acuerdo con (el|la)|"
    r"el texto (afirma|sostiene|dice|se[nñ]ala)", re.IGNORECASE)


def revisar_apoyo(margen: float) -> list[str]:
    hallazgos = []
    for prueba, banco in (("lectora", QUESTIONS_LECTORA), ("historia", QUESTIONS_HISTORIA)):
        for q in banco:
            clave = q.get("passage")
            if not clave or clave not in TEXTOS or not PIDE_TEXTO.search(q["stem"]):
                continue
            cuerpo = terminos(TEXTOS[clave]["body"])

            def apoyo(t: str, cuerpo: set[str] = cuerpo) -> float:
                w = terminos(t)
                return len(w & cuerpo) / len(w) if w else 0.0

            correcta = next(a for a in q["alternatives"] if a["is_correct"])
            ac = apoyo(correcta["text"])
            mejor = max((apoyo(a["text"]), a["text"])
                        for a in q["alternatives"] if not a["is_correct"])
            if mejor[0] > ac + margen:
                hallazgos.append(
                    f"[{prueba}/{q['skill_node']}] ({clave}) correcta {ac:.2f} "
                    f"vs distractor {mejor[0]:.2f}\n"
                    f"      {re.sub(r'\\s+', ' ', q['stem'])[:100]}\n"
                    f"      OK {correcta['text'][:75]}\n"
                    f"      ?? {mejor[1][:75]}"
                )
    return hallazgos


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", choices=["duplicados", "cobertura", "estructura", "texto"])
    ap.add_argument("--umbral-stem", type=float, default=0.45)
    ap.add_argument("--umbral-respuesta", type=float, default=0.50)
    ap.add_argument("--margen-texto", type=float, default=0.30)
    ap.add_argument("--detalle", type=int, default=15)
    args = ap.parse_args()

    total = sum(len(b) for b in BANCOS.values())
    print(f"banco: {total} preguntas · {len(TEXTOS)} textos base\n")

    def mostrar(titulo: str, items: list[str]) -> None:
        print(f"== {titulo}: {len(items)}")
        for x in items[: args.detalle]:
            print(f"   · {x}")
        if len(items) > args.detalle:
            print(f"   ... y {len(items) - args.detalle} mas")
        print()

    if args.solo in (None, "estructura"):
        fallas = revisar_estructura()
        print(f"== estructura: {sum(len(v) for v in fallas.values())} hallazgos")
        for tipo, casos in sorted(fallas.items(), key=lambda kv: -len(kv[1])):
            print(f"   {len(casos):5d}  {tipo}")
            for c in casos[:5]:
                print(f"          {c}")
        if not fallas:
            print("   sin hallazgos")
        print()

    if args.solo in (None, "cobertura"):
        resumen, faltantes = revisar_cobertura()
        print("== cobertura de aritmetica")
        for linea in resumen:
            print(f"   {linea}")
        print(f"   sin recomprobar: {len(faltantes)}")
        for f in faltantes[: args.detalle]:
            print(f"          {f}")
        print()

    if args.solo in (None, "duplicados"):
        mostrar("duplicados por parafrasis",
                revisar_duplicados(args.umbral_stem, args.umbral_respuesta))

    if args.solo in (None, "texto"):
        mostrar("la correcta se apoya menos en el texto que un distractor",
                revisar_apoyo(args.margen_texto))

    print("Ninguno de estos hallazgos es un defecto por si solo: son indicios "
          "para mirar. Los defectos duros los caza verificar_banco.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
