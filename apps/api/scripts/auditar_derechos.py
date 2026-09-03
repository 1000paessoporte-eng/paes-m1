"""Compara el banco completo contra las pruebas oficiales del DEMRE.

Por que existe
--------------
Las preguntas liberadas del DEMRE son obra con derechos de la Universidad de
Chile, y este producto cobra. El banco de 1000paes se escribe replicando
temario, formato y nivel, nunca el contenido literal. Este script existe para
poder DEMOSTRARLO con un informe fechado, en vez de afirmarlo.

Que mide
--------
La coincidencia literal mas larga, en palabras consecutivas, entre cada texto
del banco y el corpus de folletos oficiales. Se normaliza antes de comparar
(minusculas, sin tildes, sin puntuacion, espacios colapsados), de modo que un
cambio cosmetico no esconda una copia.

Como leer el resultado
----------------------
- Coincidencias de 12 palabras o mas: BANDERA ROJA. Hay que leer la pregunta y
  reescribirla.
- De 8 a 11 palabras: revisar a ojo. Suele ser lenguaje de prueba.
- 7 o menos: ruido. "cual de las siguientes afirmaciones es correcta" aparece
  en toda prueba de seleccion multiple del mundo y no es expresion protegible.

Uso
---
    PYTHONIOENCODING=utf-8 python -m uv run --with pypdf python \\
        scripts/auditar_derechos.py [--umbral 12] [--informe ruta.md]

Los folletos oficiales se buscan en las carpetas de CORPUS. Si falta alguno,
el informe lo dice: un informe con corpus incompleto no sirve como respaldo.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Carpetas donde viven los folletos oficiales bajados del DEMRE. No entran al
# repo: son material con derechos y ademas pesan.
CORPUS = [
    Path.home() / "Downloads",
    Path.home() / "Desktop" / "temarios-pruebas paes",
]

#: Solo las PRUEBAS, no los temarios. Un temario es un listado de contenidos y
#: coincidir con el no es un problema: es el objetivo del banco.
PATRON_PRUEBA = re.compile(r"paes.*(regular|invierno).*p20\d\d\.pdf$", re.I)
PATRON_TEMARIO = re.compile(r"temario", re.I)

N_MAX = 20  # cota superior de la coincidencia que se busca
N_MIN = 6   # por debajo de esto todo es lenguaje formulario


def normalizar(texto: str) -> list[str]:
    """Deja el texto en palabras comparables: sin tildes, sin puntuacion."""
    t = unicodedata.normalize("NFKD", texto.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9ñ ]+", " ", t)
    return t.split()


def ngramas(palabras: list[str], n: int):
    for i in range(len(palabras) - n + 1):
        yield " ".join(palabras[i : i + n])


def cargar_corpus() -> tuple[list[str], list[Path], list[Path]]:
    from pypdf import PdfReader

    pruebas, temarios = [], []
    for carpeta in CORPUS:
        if not carpeta.is_dir():
            continue
        for pdf in sorted(carpeta.glob("*.pdf")):
            if PATRON_TEMARIO.search(pdf.name):
                temarios.append(pdf)
            elif PATRON_PRUEBA.search(pdf.name):
                pruebas.append(pdf)

    textos = []
    for pdf in pruebas:
        try:
            lector = PdfReader(str(pdf))
            textos.append("\n".join(p.extract_text() or "" for p in lector.pages))
        except Exception as e:  # noqa: BLE001
            print(f"  !! no se pudo leer {pdf.name}: {e}")
    return textos, pruebas, temarios


def indexar(textos: list[str]) -> dict[int, set[str]]:
    """Un conjunto de n-gramas por cada largo, del corpus oficial."""
    indices = {n: set() for n in range(N_MIN, N_MAX + 1)}
    for texto in textos:
        palabras = normalizar(texto)
        for n in indices:
            indices[n].update(ngramas(palabras, n))
    return indices


def coincidencia_maxima(texto: str, indices: dict[int, set[str]]) -> tuple[int, str]:
    """El n-grama compartido mas largo entre `texto` y el corpus."""
    palabras = normalizar(texto)
    mejor_n, mejor_txt = 0, ""
    for n in range(N_MAX, N_MIN - 1, -1):
        if len(palabras) < n:
            continue
        for g in ngramas(palabras, n):
            if g in indices[n]:
                return n, g
        if mejor_n:
            break
    return mejor_n, mejor_txt


def piezas_del_banco():
    """Todo lo que un estudiante llega a leer, con su procedencia."""
    from paes_api.seed_data import (
        PASSAGES,
        PASSAGES_HISTORIA,
        QUESTIONS,
        QUESTIONS_CIENCIAS,
        QUESTIONS_HISTORIA,
        QUESTIONS_LECTORA,
    )

    bancos = [
        ("matematica", QUESTIONS),
        ("lectora", QUESTIONS_LECTORA),
        ("ciencias", QUESTIONS_CIENCIAS),
        ("historia", QUESTIONS_HISTORIA),
    ]
    for prueba, banco in bancos:
        for q in banco:
            partes = [q["stem"], q.get("explanation", "")]
            partes += [a["text"] for a in q["alternatives"]]
            partes += [a["justification"] or "" for a in q["alternatives"]]
            yield prueba, "pregunta", q["stem"][:90], " ".join(partes)

    for prueba, pasajes in (("lectora", PASSAGES), ("historia", PASSAGES_HISTORIA)):
        for p in pasajes:
            yield prueba, "texto", p["title"][:90], p["body"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--umbral", type=int, default=12,
                    help="palabras consecutivas que se consideran bandera roja")
    ap.add_argument("--informe", default="", help="ruta del informe markdown")
    args = ap.parse_args()

    print("leyendo folletos oficiales...")
    textos, pruebas, temarios = cargar_corpus()
    if not textos:
        print("SIN CORPUS: no se encontro ninguna prueba oficial. El informe "
              "no sirve como respaldo.")
        return 2
    print(f"  {len(pruebas)} pruebas oficiales, {len(temarios)} temarios "
          f"(los temarios NO entran a la comparacion)")

    indices = indexar(textos)
    print(f"  {len(indices[args.umbral]):,} secuencias de {args.umbral} "
          f"palabras en el corpus".replace(",", "."))

    print("comparando el banco...")
    reparto: dict[int, int] = {}
    rojas, ambar = [], []
    total = 0
    for prueba, tipo, etiqueta, texto in piezas_del_banco():
        total += 1
        n, g = coincidencia_maxima(texto, indices)
        reparto[n] = reparto.get(n, 0) + 1
        if n >= args.umbral:
            rojas.append((prueba, tipo, etiqueta, n, g))
        elif n >= 8:
            ambar.append((prueba, tipo, etiqueta, n, g))

    lineas = []
    add = lineas.append
    hoy = dt.date.today().isoformat()
    add(f"# Auditoria de coincidencia literal con las pruebas oficiales\n")
    add(f"Fecha: **{hoy}**  ·  Umbral de bandera roja: **{args.umbral} palabras "
        f"consecutivas**\n")
    add("## Corpus oficial comparado\n")
    for p in pruebas:
        add(f"- `{p.name}`")
    add("")
    add(f"Se excluyen los {len(temarios)} temarios: un temario es un listado de "
        "contenidos y coincidir con el es el objetivo del banco, no un defecto.\n")
    add("## Metodo\n")
    add("Los textos se normalizan (minusculas, sin tildes, sin puntuacion) y se "
        "compara la secuencia de palabras consecutivas mas larga que el banco "
        "comparte con el corpus. Se revisa el enunciado, la explicacion, las "
        "cuatro alternativas con sus justificaciones, y los textos base.\n")
    add("## Resultado\n")
    add(f"- Piezas del banco revisadas: **{total:,}**".replace(",", "."))
    add(f"- Coincidencias de {args.umbral} palabras o mas: **{len(rojas)}**")
    add(f"- Coincidencias de 8 a {args.umbral - 1} palabras: **{len(ambar)}**\n")
    add("### Reparto de la coincidencia mas larga\n")
    add("| Palabras consecutivas | Piezas |")
    add("|---|---|")
    for n in sorted(reparto, reverse=True):
        etq = "sin coincidencia de 6 o mas" if n == 0 else str(n)
        add(f"| {etq} | {reparto[n]} |")
    add("")
    add("Las coincidencias de 6 y 7 palabras son lenguaje de prueba de seleccion "
        "multiple (\"cual de las siguientes afirmaciones es correcta\", \"de "
        "acuerdo con el texto leido\"). No son expresion protegible: aparecen en "
        "cualquier prueba del mundo.\n")

    if rojas:
        add("### BANDERAS ROJAS\n")
        for prueba, tipo, etiqueta, n, g in rojas:
            add(f"- **{prueba} / {tipo}** ({n} palabras) — {etiqueta}")
            add(f"  - coincidencia: `{g}`")
        add("")
    else:
        add("### Banderas rojas\n")
        add(f"**Ninguna.** No hay una sola secuencia de {args.umbral} palabras "
            "consecutivas en comun entre el banco y las pruebas oficiales "
            "comparadas.\n")

    if ambar:
        add("### Coincidencias intermedias (8 a 11 palabras)\n")
        for prueba, tipo, etiqueta, n, g in sorted(ambar, key=lambda x: -x[3])[:40]:
            add(f"- {prueba} / {tipo} ({n}) — `{g}`")
        if len(ambar) > 40:
            add(f"- ... y {len(ambar) - 40} mas")
        add("")

    add("## Alcance y limites\n")
    add("- El corpus son los folletos que estan en disco. **No incluye todas las "
        "pruebas liberadas por el DEMRE**: un informe limpio dice que no hay "
        "copia respecto de ESTOS folletos.")
    add("- No hay folleto oficial de M2 en el corpus, asi que los nodos "
        "exclusivos de M2 quedan comparados solo contra las pruebas de M1.")
    add("- La comparacion es literal. No detecta una pregunta que replique la "
        "ESTRUCTURA de una oficial con otros numeros y otras palabras; eso se "
        "revisa leyendo.")
    add("- Las figuras no se comparan: son archivos SVG propios del repo, "
        "dibujados para cada pregunta.")

    informe = "\n".join(lineas)
    destino = Path(args.informe) if args.informe else (
        Path(__file__).resolve().parents[3] / "docs" / f"auditoria-derechos-{hoy}.md"
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(informe, encoding="utf-8", newline="\n")

    print()
    print(f"piezas revisadas: {total}")
    print(f"banderas rojas ({args.umbral}+ palabras): {len(rojas)}")
    print(f"intermedias (8-{args.umbral - 1}): {len(ambar)}")
    print(f"informe: {destino}")
    return 1 if rojas else 0


if __name__ == "__main__":
    raise SystemExit(main())
