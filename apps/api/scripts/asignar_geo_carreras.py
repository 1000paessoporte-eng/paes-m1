"""Asigna región y comuna a cada carrera cruzando con la base oficial del SIES.

    uv run python scripts/asignar_geo_carreras.py <base_sies.csv>

Reescribe `src/paes_api/data/carreras_2026.json` agregando `region` y `comuna` a
cada carrera, e imprime un informe de cobertura. Las carreras sin cruce quedan
con `region`/`comuna` en null.

POR QUÉ EXISTE
--------------
El catálogo de carreras sale del PDF del DEMRE, que trae `sede` como texto libre
(mezcla ciudades, campus y hasta regiones) y ninguna columna de comuna o región.
Para filtrar el catálogo por ubicación hace falta ese dato, y no se puede
inventar: sale de la **base de matrícula en Educación Superior del SIES
(Mineduc)**, que publica región, provincia y comuna de la sede de cada programa.

    https://datosabiertos.mineduc.cl/matricula-en-educacion-superior/
    (archivo Matricula-Ed-Superior-2025.rar -> el .csv separado por ';')

La base cruda pesa ~900 MB y no se versiona, igual que el PDF del DEMRE: se
descarga aparte y se pasa como argumento. Lo versionado es el resultado del
cruce dentro de `carreras_2026.json`.

CÓMO SE CRUZA
-------------
El DEMRE y el SIES no comparten un código común (el `codigo` del DEMRE es de
postulación; el SIES usa su propio código de institución), así que el cruce es
por nombre normalizado de **institución + carrera**, desambiguando por sede.

- La normalización quita tildes, puntuación y mayúsculas (`O'Higgins` ->
  `OHIGGINS`), y del nombre de carrera se quitan los sufijos entre paréntesis
  que agrega el DEMRE (`ACTUACIÓN (PE) (25)` -> `ACTUACION`).
- Seis universidades tienen nombre distinto entre las dos fuentes (el SIES dice
  "Técnica Federico Santa María", el DEMRE "Federico Santa María"); ese puñado
  se reconcilia con `ALIAS`, que empareja dos nombres OFICIALES, no inventa uno.

REGLA DE CALIDAD: no se inventa comuna
--------------------------------------
Una universidad dicta la misma carrera en varias sedes/comunas. Cuando la sede
del DEMRE no alcanza para decidir cuál, se asigna solo la **región** si es única
entre las candidatas, y la comuna queda en null. Nunca se elige una comuna "a
dedo": es preferible que falte a que aparezca una equivocada. La comuna se
asigna solo cuando hay una sola candidata o cuando la sede del DEMRE la
identifica sin ambigüedad.
"""

import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

csv.field_size_limit(10_000_000)

DATA = Path(__file__).resolve().parents[1] / "src/paes_api/data/carreras_2026.json"

#: Universidades cuyo nombre difiere entre el DEMRE y el SIES. Clave: nombre
#: normalizado como lo escribe el DEMRE; valor: como lo escribe el SIES. Los dos
#: lados son nombres oficiales; esto solo los empareja.
ALIAS_CRUDO = {
    "UNIVERSIDAD ARTURO PRAT DE CHILE": "UNIVERSIDAD ARTURO PRAT",
    "UNIVERSIDAD CATÓLICA SILVA HENRÍQUEZ": (
        "UNIVERSIDAD CATOLICA CARDENAL RAUL SILVA HENRIQUEZ"
    ),
    "UNIVERSIDAD CENTRAL": "UNIVERSIDAD CENTRAL DE CHILE",
    "UNIVERSIDAD DE PLAYA ANCHA": (
        "UNIVERSIDAD DE PLAYA ANCHA DE CIENCIAS DE LA EDUCACION"
    ),
    "UNIVERSIDAD FEDERICO SANTA MARÍA": "UNIVERSIDAD TECNICA FEDERICO SANTA MARIA",
    "UNIVERSIDAD VIÑA DEL MAR": "UNIVERSIDAD DE VIÑA DEL MAR",
}


def norm(s: str) -> str:
    """Sin tildes, sin puntuación, en mayúsculas y con espacios colapsados.

    Los apóstrofes se pasan a espacio ANTES de quitar lo no-ASCII: si no, el
    apóstrofe tipográfico `’` (U+2019, el que usa el PDF del DEMRE) lo borra el
    encode ASCII y "O’Higgins" queda "OHIGGINS", mientras el apóstrofe recto `'`
    del SIES lo vuelve espacio y da "O HIGGINS". Dos formas del mismo nombre que
    no cruzaban. Igualadas acá, "O'Higgins" siempre es "O HIGGINS".
    """
    s = unicodedata.normalize("NFKD", s or "").replace("’", " ").replace("'", " ")
    s = s.encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Z0-9 ]", " ", s.upper())
    return " ".join(s.split())


def limpia_carrera(s: str) -> str:
    """El nombre de carrera sin los sufijos entre paréntesis del DEMRE."""
    return norm(re.sub(r"\([^)]*\)", " ", s))


ALIAS = {norm(k): norm(v) for k, v in ALIAS_CRUDO.items()}

#: El SIES escribe el nombre largo de la región de O'Higgins. Se canoniza al
#: nombre corto para que quede alineado con `ORDEN_REGIONES` del servicio y con
#: cómo lo escribe todo el resto del país.
NOMBRE_REGION_CANONICO = {"Lib. Gral. B. O'Higgins": "O'Higgins"}

#: Rescate curado para carreras que el SIES no resuelve por el parseo roto del
#: DEMRE (sede "10", nombre de carrera partido) o campus que el SIES nombra
#: distinto. Cada fila es geografía verificable, no un dato inventado: cada
#: campus está donde dice. Formato: (institución, palabra en la sede o None para
#: cualquier sede) -> (región, comuna). Las palabras específicas van ANTES del
#: None de la misma institución. Se aplican solo como último recurso, cuando el
#: cruce con el SIES ya falló. Universidades cuya sede es genuinamente ambigua
#: (UCN entre Antofagasta y Coquimbo, Autónoma entre tres regiones) se dejan
#: fuera a propósito: mejor sin geo que con una comuna equivocada.
OVERRIDES: list[tuple[str, str | None, str, str]] = [
    ("UNIVERSIDAD DE O HIGGINS", "COLCHAGUA", "O'Higgins", "SAN FERNANDO"),
    ("UNIVERSIDAD DE O HIGGINS", None, "O'Higgins", "RANCAGUA"),
    ("UNIVERSIDAD AUSTRAL DE CHILE", "MIRAFLORES", "Los Ríos", "VALDIVIA"),
    ("UNIVERSIDAD AUSTRAL DE CHILE", "ISLA", "Los Ríos", "VALDIVIA"),
    ("UNIVERSIDAD AUSTRAL DE CHILE", "10", "Los Ríos", "VALDIVIA"),
    ("UNIVERSIDAD DE VALPARAISO", None, "Valparaíso", "VALPARAISO"),
    ("UNIVERSIDAD DE LAS AMERICAS", "SANTIAGO CENTRO", "Metropolitana", "SANTIAGO"),
    ("UNIVERSIDAD TECNOLOGICA METROPOLITANA", "NUNOA", "Metropolitana", "ÑUÑOA"),
    ("UNIVERSIDAD ACADEMIA DE HUMANISMO CRISTIANO", "CONDELL", "Metropolitana", "PROVIDENCIA"),
    ("UNIVERSIDAD DE ATACAMA", None, "Atacama", "COPIAPO"),
]


def institucion(universidad: str) -> str:
    n = norm(universidad)
    return ALIAS.get(n, n)


def _override(inst: str, sede_norm: str) -> tuple[str, str] | None:
    """La geografía curada para una carrera que el SIES no resolvió, o None."""
    for inst_ov, palabra, region, comuna in OVERRIDES:
        if inst == inst_ov and (palabra is None or palabra in sede_norm):
            return region, comuna
    return None


def construir_indices(csv_path: Path):
    """Una pasada por la base del SIES arma los índices que necesita el cruce."""
    # (inst, carrera) -> Counter[(sede_norm, region, comuna)]
    por_inst_carr: dict[tuple[str, str], Counter] = defaultdict(Counter)
    # (inst, sede) -> Counter[(region, comuna)]
    por_inst_sede: dict[tuple[str, str], Counter] = defaultdict(Counter)
    # inst -> Counter[(region, comuna)]
    por_inst: dict[str, Counter] = defaultdict(Counter)
    # comuna_norm -> Counter[(region, comuna_original)]  (rescate por ciudad)
    por_comuna: dict[str, Counter] = defaultdict(Counter)

    with open(csv_path, encoding="utf-8", errors="replace", newline="") as f:
        for row in csv.DictReader(f, delimiter=";"):
            reg = (row["region_sede"] or "").strip()
            com = (row["comuna_sede"] or "").strip()
            if not reg or not com:
                continue
            reg = NOMBRE_REGION_CANONICO.get(reg, reg)
            i = institucion(row["nomb_inst"])
            sd = norm(row["nomb_sede"])
            kk = limpia_carrera(row["nomb_carrera"])
            por_inst_carr[(i, kk)][(sd, reg, com)] += 1
            por_inst_sede[(i, sd)][(reg, com)] += 1
            por_inst[i][(reg, com)] += 1
            por_comuna[norm(com)][(reg, com)] += 1
    return por_inst_carr, por_inst_sede, por_inst, por_comuna


def resolver(universidad, sede, carrera, idx):
    """Devuelve (metodo, region, comuna). region/comuna pueden ser None."""
    por_inst_carr, por_inst_sede, por_inst, por_comuna = idx
    i = institucion(universidad)
    sd = norm(sede)
    kk = limpia_carrera(carrera)

    detalle = por_inst_carr.get((i, kk))
    if detalle:
        geos = {(r, c) for (_, r, c) in detalle}
        if len(geos) == 1:
            r, c = next(iter(geos))
            return "carrera", r, c
        # Varias sedes: intentar que la sede del DEMRE elija una.
        for (ss, r, c) in detalle:
            if sd and (sd in ss or ss in sd or sd == norm(c)):
                return "carrera+sede", r, c
        # No se puede decidir la comuna. Si la región es única, va la región.
        regiones = {r for (r, _) in geos}
        if len(regiones) == 1:
            return "carrera(region)", next(iter(regiones)), None
        # Carrera ambigua entre regiones: no se rinde acá, cae a los fallbacks
        # comunes de abajo (sede=comuna, override) como si no la hubiera hallado.

    # Fallbacks comunes: valen tanto si la carrera no está en el SIES como si
    # está pero quedó ambigua. La sede del DEMRE suele ser una ciudad/comuna.
    if sd in por_comuna:
        r, c = por_comuna[sd].most_common(1)[0][0]
        return "sede=comuna", r, c

    sede_hit = por_inst_sede.get((i, sd))
    if sede_hit and len({g for g in sede_hit}) == 1:
        r, c = next(iter(sede_hit))
        return "inst+sede", r, c

    # La institución dicta en una sola comuna: esa es.
    inst_hit = por_inst.get(i)
    if inst_hit and len(inst_hit) == 1:
        r, c = next(iter(inst_hit))
        return "inst_unica", r, c

    # Último recurso: geografía curada para los casos que el SIES no resuelve
    # (parseo roto del DEMRE, campus con otro nombre). Ver `OVERRIDES`.
    ov = _override(i, sd)
    if ov is not None:
        return "override", ov[0], ov[1]

    return "sin_match", None, None


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"no existe la base del SIES: {csv_path}")
        return 2

    print(f"leyendo {csv_path.name} ...")
    idx = construir_indices(csv_path)

    datos = json.loads(DATA.read_text(encoding="utf-8"))
    metodos: Counter = Counter()
    con_comuna = con_region = 0
    sin_match = []
    for fila in datos["carreras"]:
        metodo, reg, com = resolver(
            fila["universidad"], fila["sede"], fila["carrera"], idx
        )
        metodos[metodo] += 1
        fila["region"] = reg
        fila["comuna"] = com
        if reg:
            con_region += 1
        if com:
            con_comuna += 1
        if metodo == "sin_match":
            sin_match.append(fila)

    # Mismo formato que escribe `extraer_carreras.py` (indent=1, sin newline
    # final): así el diff son solo los dos campos nuevos por carrera.
    DATA.write_text(
        json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    total = len(datos["carreras"])
    print(f"\ncarreras: {total}")
    for metodo, n in metodos.most_common():
        print(f"  {metodo:16} {n:5}  ({100 * n / total:.1f}%)")
    print(f"\ncon región: {con_region}/{total} ({100 * con_region / total:.1f}%)")
    print(f"con comuna: {con_comuna}/{total} ({100 * con_comuna / total:.1f}%)")
    print(f"sin ninguna: {len(sin_match)}")
    if sin_match:
        reporte = csv_path.parent / "carreras_sin_geo.txt"
        reporte.write_text(
            "\n".join(
                f"{c['universidad']} | {c['sede']} | {c['carrera']}" for c in sin_match
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"detalle de las sin cruce en: {reporte}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
