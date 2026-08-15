"""Extrae las ponderaciones oficiales de carreras desde el PDF del DEMRE.

    uv run python scripts/extraer_carreras.py oferta.pdf

Genera `src/paes_api/data/carreras_<proceso>.json`.

POR QUÉ ESTO EXISTE Y NO UNA TABLA ESCRITA A MANO
--------------------------------------------------
Cuánto pondera M1 en Ingeniería Civil de la Universidad de Chile no es algo que
se pueda estimar: es un dato oficial del que dependen decisiones de matrícula.
Escribirlo a mano sería inventar, y las ponderaciones cambian cada proceso.

El PDF es la fuente:
https://demre.cl/publicaciones/2026/2026-25-09-25-oferta-carreras-vacantes-ponderaciones-p2026

CÓMO SE VALIDA
--------------
Las ponderaciones de una carrera SIEMPRE suman 100. Esa es la comprobación:
una carrera cuyo parseo no suma 100 se descarta con su motivo, en vez de
entrar con datos a medias. Es preferible que una carrera falte a que aparezca
con una ponderación equivocada.

Cuando la carrera admite prueba electiva ("Historia ó Ciencias"), ambas
aparecen con el mismo peso pero solo una cuenta: por eso se resta la menor
antes de comprobar la suma.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

#: El PDF escribe el separador de electivas de tres formas distintas.
ELECTIVO = {"o", "ó", "O", "Ó"}
PESOS = ["nem", "ranking", "lectora", "m1", "historia", "ciencias", "m2"]
PROCESO = 2026
FUENTE = (
    "https://demre.cl/publicaciones/2026/"
    "2026-25-09-25-oferta-carreras-vacantes-ponderaciones-p2026"
)


def _universidad_de(pagina: str) -> str | None:
    """El nombre de la universidad, tomado del encabezado de la página.

    El encabezado trae además el título del documento impreso en vertical al
    margen, que pdftotext desarma en letras sueltas y pega al final del nombre
    ("UNIVERSIDAD ADOLFO IBÁÑEZ O FE RTA DEF IN ITIVA DE CARRE RAS..."). Se
    corta en cuanto aparece ese patrón.
    """
    lineas = [linea.strip() for linea in pagina.split("\n") if linea.strip()]
    nombre: list[str] = []
    for linea in lineas[:4]:
        if linea.upper().startswith(("PONDERACIÓN", "DESCRIPCIÓN", "COD")):
            break
        nombre.append(linea)
    if not nombre:
        return None

    texto = " ".join(nombre)
    # El título vertical siempre empieza con la "O" de OFERTA separada del resto.
    texto = re.split(r"\s+O\s*FE\s*RTA|\s+OFERTA\s+DEF", texto)[0]
    # Y por si quedaran restos: una universidad nunca tiene letras sueltas.
    texto = re.sub(r"(\s+[A-Z]){4,}\s*$", "", texto)
    return " ".join(texto.split()).strip()


def _num(token: str) -> float | None:
    if token in ("---", "") or token in ELECTIVO:
        return None
    try:
        return float(token.replace(",", "."))
    except ValueError:
        return None


def extraer(pdf: Path) -> tuple[list[dict], list[tuple[str, str]]]:
    texto = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True, text=True, check=True,
    ).stdout

    filas: list[dict] = []
    descartes: list[tuple[str, str]] = []
    universidad = None

    for pagina in texto.split("\f"):
        if not re.search(r"^\d{5} ", pagina, re.MULTILINE):
            continue
        nombre_u = _universidad_de(pagina)
        if nombre_u and len(nombre_u) > 8:
            universidad = nombre_u

        lineas = pagina.split("\n")
        for i, linea in enumerate(lineas):
            m = re.match(r"^(\d{5})\s{2,}(.+)$", linea)
            if not m:
                continue
            codigo = m.group(1)
            campos = re.split(r"\s{2,}", m.group(2).strip())

            if len(campos) >= 10:
                carrera, datos = campos[0], campos[1:]
            else:
                # Nombre largo: se parte en dos líneas y los datos quedan en la
                # siguiente.
                previo = lineas[i - 1].strip() if i > 0 else ""
                carrera = f"{previo} {campos[0]}".strip()
                cruda = lineas[i + 1] if i + 1 < len(lineas) else ""
                datos = re.split(r"\s{2,}", cruda.strip())

            if len(datos) < 9:
                descartes.append((codigo, "columnas insuficientes"))
                continue

            sede, resto = datos[0], datos[1:]
            electivo = any(c in ELECTIVO for c in resto)
            resto = [c for c in resto if c not in ELECTIVO]

            ponderaciones = {
                clave: (_num(resto[j]) if j < len(resto) else None)
                for j, clave in enumerate(PESOS)
            }

            # Tras los siete pesos puede venir PRUEBA ESPECIAL (una ponderación,
            # ≤100) o directamente el PUNTAJE PONDERADO MÍNIMO (≥150). No todas
            # las universidades traen la columna de prueba especial, así que se
            # distingue por magnitud y no por posición.
            siguiente = _num(resto[7]) if len(resto) > 7 else None
            especial = siguiente if (siguiente is not None and siguiente <= 100) else None

            total = sum(v or 0 for v in ponderaciones.values()) + (especial or 0)
            if electivo:
                total -= min(ponderaciones["historia"] or 0, ponderaciones["ciencias"] or 0)

            if abs(total - 100) > 0.51:
                descartes.append(
                    (codigo, f"{universidad} | {carrera} | las ponderaciones suman {total:g}")
                )
                continue

            filas.append({
                "codigo": codigo,
                "universidad": universidad,
                "carrera": carrera,
                "sede": sede,
                "electivo_alternativo": electivo,
                "prueba_especial": especial,
                **ponderaciones,
            })

    return filas, descartes


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    pdf = Path(sys.argv[1])
    if not pdf.exists():
        print(f"No existe {pdf}")
        return 1

    filas, descartes = extraer(pdf)
    salida = Path(__file__).resolve().parents[1] / "src/paes_api/data" / f"carreras_{PROCESO}.json"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(
        json.dumps(
            {"proceso": PROCESO, "fuente": FUENTE, "carreras": filas},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )

    universidades = len({f["universidad"] for f in filas})
    print(f"{len(filas)} carreras de {universidades} universidades → {salida.name}")
    print(f"{len(descartes)} descartadas por no validar (ver detalle con --detalle)")
    if "--detalle" in sys.argv:
        for codigo, motivo in descartes:
            print(f"  {codigo}: {motivo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
