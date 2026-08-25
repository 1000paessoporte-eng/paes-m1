"""Deja la base igual a seed_data.py. seed.py solo INSERTA; esto reconcilia.

`scripts/seed.py` salta cualquier pregunta cuyo enunciado ya exista, y esa
regla —la que lo hace idempotente— tiene un costo: no publica nada de lo que
cambia SIN cambiar el enunciado. Corriendo solo seed.py no llegan a produccion
los cambios de dificultad, ni los distractores corregidos, ni las
justificaciones reescritas, ni el cambio de prueba de un nodo (M1 a M2). Y
peor: cuando una pregunta se reescribe, la version vieja queda VIVA, porque la
nueva tiene otro enunciado y entra como si fuera adicional.

Este script corrige en su lugar todo lo que cambio sin cambiar de enunciado y
borra lo que ya no esta en seed_data. La secuencia para publicar es de DOS
pasos:

    seed.py  ->  sincronizar.py --aplicar

El seed crea los nodos y textos nuevos e inserta las preguntas nuevas; el sync
corrige y limpia. Nada falta en ningun momento intermedio.

POR QUE NO HAY UN TERCER PASO (y por que importa).
Hasta el 2026-08-23 la secuencia era `seed -> sincronizar -> seed`: el sync
BORRABA las preguntas cuyas alternativas habian cambiado y el ultimo seed las
reponia con otro id. Eso dejaba el sitio en produccion varios minutos con menos
preguntas de las que debe —el 2026-08-19 M1 se vio en 991 en vez de 1088— y
quien armara un ensayo dentro de esa ventana lo armaba sobre un banco
incompleto. Ademas la cascada de claves foraneas se llevaba puestas filas de
ensayos ya rendidos: la pregunta volvia con id nuevo, asi que el intento viejo
perdia esa pregunta y su respuesta.

Ahora una pregunta que solo cambio de alternativas CONSERVA SU ID: se corrigen
las filas de `alternatives` que siguen valiendo, se borran las que ya no estan
y se insertan las nuevas en las etiquetas que quedaron libres. La pregunta no
desaparece en ningun instante y el historial de ensayos sobrevive. Lo unico que
se sigue borrando de verdad es lo que de verdad se fue de seed_data.

TRAMPA: la base guarda el NOMBRE del enum ("FACIL", "M1"), no el valor que usa
seed_data ("facil"). Por eso la comparacion va en mayusculas.

Uso:
    DATABASE_URL="<string directo>" uv run python scripts/sincronizar.py
Sin --aplicar solo informa; con --aplicar escribe, dejando antes un respaldo
JSON de todo lo que va a borrar.
"""
import datetime
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

#: Etiquetas posibles de una alternativa, en orden. La base guarda `label` como
#: un solo caracter y la interfaz muestra ese orden.
LABELS = ("A", "B", "C", "D", "E")


def planificar_alternativas(actuales, deseadas):
    """Como dejar las alternativas de UNA pregunta iguales a seed_data.

    Devuelve `(corregir, borrar, insertar)` sin tocar la pregunta misma, que
    es el punto: su id sobrevive y con el sobreviven los ensayos que la usaron.

    - `actuales`: filas de la base, `(id, label, texto, es_correcta, justificacion)`.
    - `deseadas`: lo que dice seed_data, dicts con `text`, `is_correct` y
      `justification`.

    El emparejamiento va por TEXTO, que es lo unico estable entre las dos
    fuentes: la base no guarda de donde salio cada fila. Una alternativa cuyo
    texto sigue vivo conserva su id y su etiqueta aunque le hayan corregido la
    justificacion o le hayan movido la marca de correcta; las que ya no estan
    se borran y las nuevas ocupan las etiquetas que quedaron libres.

    Nunca se reescribe el TEXTO de una fila existente, aunque saldria mas
    barato. Una respuesta ya rendida apunta a esa fila: cambiarle el texto por
    debajo haria que un intento del mes pasado afirme que el alumno eligio algo
    que nunca vio, y si ademas cambia `is_correct`, le cambia el puntaje.
    Borrar es honesto; reescribir es falsificar.
    """
    pendientes: dict[str, list[dict]] = {}
    for d in deseadas:
        pendientes.setdefault(d["text"], []).append(d)

    corregir: list[tuple[int, bool, str | None]] = []
    borrar: list[int] = []
    ocupadas: set[str] = set()

    for aid, label, texto, es_correcta, justificacion in actuales:
        iguales = pendientes.get(texto)
        if not iguales:
            borrar.append(aid)
            continue
        d = iguales.pop(0)
        if not iguales:
            del pendientes[texto]
        ocupadas.add(label)
        if (bool(es_correcta), justificacion) != (
            bool(d["is_correct"]),
            d["justification"],
        ):
            corregir.append((aid, bool(d["is_correct"]), d["justification"]))

    libres = [x for x in LABELS[: len(deseadas)] if x not in ocupadas]
    insertar: list[tuple[str, str, bool, str | None]] = []
    faltantes = [d for lista in pendientes.values() for d in lista]
    if len(faltantes) > len(libres):
        raise ValueError(
            f"no alcanzan las etiquetas: {len(faltantes)} alternativas nuevas "
            f"para {len(libres)} libres (la pregunta tiene {len(actuales)} "
            f"filas en la base y seed_data define {len(deseadas)})"
        )
    for d, label in zip(faltantes, libres, strict=False):
        insertar.append((label, d["text"], bool(d["is_correct"]), d["justification"]))

    return corregir, borrar, insertar


def estado_deseado(questions, titulos_por_clave):
    """Lo que seed_data dice que tiene que haber, indexado por enunciado."""
    deseado = {}
    for q in questions:
        deseado[q["stem"]] = {
            "nodo": q["skill_node"],
            "dificultad": q["difficulty"].upper(),
            "explicacion": q["explanation"],
            "imagen": q.get("image_url"),
            "texto_base": titulos_por_clave.get(q.get("passage")),
            "alternativas": [
                {
                    "text": a["text"],
                    "is_correct": bool(a["is_correct"]),
                    "justification": a["justification"],
                }
                for a in q["alternatives"]
            ],
        }
    return deseado


def main() -> None:
    import psycopg

    from paes_api.seed_data import (
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

    aplicar = "--aplicar" in sys.argv
    url = os.environ["DATABASE_URL"].replace("postgresql+psycopg://", "postgresql://")

    # Las cinco pruebas entran a la comparacion. Si aqui faltara una, sus nodos
    # apareceran como "no estan en seed_data" y el script se ofreceria a
    # borrarlos: la lista tiene que estar COMPLETA.
    subject_por_nodo = {}
    #: code -> (nombre, eje, tier) tal como los define seed_data.
    ficha_por_nodo = {}
    for nodos, prueba in (
        (SKILL_NODES, "M1"),
        (SKILL_NODES_M2, "M2"),
        (SKILL_NODES_LECTORA, "LECTORA"),
        (SKILL_NODES_CIENCIAS, "CIENCIAS"),
        (SKILL_NODES_HISTORIA, "HISTORIA"),
    ):
        for n in nodos:
            subject_por_nodo[n[0]] = prueba
            ficha_por_nodo[n[0]] = (n[1], n[2], n[3])

    titulos_por_clave = {p["key"]: p["title"] for p in PASSAGES + PASSAGES_HISTORIA}
    deseado = estado_deseado(
        QUESTIONS + QUESTIONS_LECTORA + QUESTIONS_CIENCIAS + QUESTIONS_HISTORIA,
        titulos_por_clave,
    )

    with psycopg.connect(url, connect_timeout=30) as c, c.cursor() as cur:
        cur.execute(
            """select q.id, q.stem, s.code, q.difficulty::text, q.explanation,
                       q.image_url, p.title
                 from questions q
                 join skill_nodes s on s.id = q.skill_node_id
                 left join reading_passages p on p.id = q.passage_id"""
        )
        filas = cur.fetchall()
        cur.execute(
            "select question_id, id, label, text, is_correct, distractor_justification"
            "  from alternatives"
        )
        porq: dict[int, list] = {}
        for qid, aid, label, txt, ok, justif in cur.fetchall():
            porq.setdefault(qid, []).append((aid, label, txt, ok, justif))

        sobran, difieren_alt, difieren_meta = [], [], []
        for qid, stem, code, dif, explicacion, imagen, titulo in filas:
            objetivo = deseado.get(stem)
            if objetivo is None:
                sobran.append((qid, code, stem))
                continue
            corregir, borrar, insertar = planificar_alternativas(
                sorted(porq.get(qid, [])), objetivo["alternativas"]
            )
            if corregir or borrar or insertar:
                difieren_alt.append((qid, stem, corregir, borrar, insertar))
            if (code, dif, explicacion, imagen, titulo) != (
                objetivo["nodo"],
                objetivo["dificultad"],
                objetivo["explicacion"],
                objetivo["imagen"],
                objetivo["texto_base"],
            ):
                difieren_meta.append((qid, objetivo, code, dif, titulo))

        cur.execute(
            "select id, code, subject::text, name, axis::text, tier from skill_nodes"
        )
        nodos_bd = cur.fetchall()
        nodos_mal = [
            (cod, sub, subject_por_nodo[cod])
            for _, cod, sub, *_ in nodos_bd
            if cod in subject_por_nodo and sub != subject_por_nodo[cod]
        ]
        # Nombre, eje y tier tampoco llegaban nunca a produccion: seed.py salta
        # el nodo si el code ya existe, asi que renombrar un nodo en seed_data
        # no cambiaba nada de lo que ve el alumno en el arbol.
        nodos_ficha = [
            (cod, ficha_por_nodo[cod], (nom, eje.lower(), tier))
            for _, cod, _sub, nom, eje, tier in nodos_bd
            if cod in ficha_por_nodo
            and ficha_por_nodo[cod] != (nom, eje.lower(), tier)
        ]
        # Un nodo que ya no esta en seed_data se fue del arbol (una fusion, un
        # nodo que resulto no ser del temario). Antes esto no se detectaba: el
        # nodo quedaba vivo y vacio, visible en el arbol para siempre.
        nodos_sobran = [
            (nid, cod) for nid, cod, *_ in nodos_bd if cod not in subject_por_nodo
        ]

        titulos_ok = {p["title"] for p in PASSAGES + PASSAGES_HISTORIA}
        cur.execute("select id, title from reading_passages")
        textos_sobran = [(i, t) for i, t in cur.fetchall() if t not in titulos_ok]

        faltan = set(deseado) - {f[1] for f in filas}

        alt_corregidas = sum(len(d[2]) for d in difieren_alt)
        alt_borradas = sum(len(d[3]) for d in difieren_alt)
        alt_nuevas = sum(len(d[4]) for d in difieren_alt)

        print(f"preguntas en produccion: {len(filas)}")
        print(f"  sobran (ya no estan en seed_data):        {len(sobran)}")
        print(f"  con alternativas distintas (se reparan):  {len(difieren_alt)}")
        print(
            f"    -> {alt_corregidas} alternativas corregidas, "
            f"{alt_borradas} borradas, {alt_nuevas} nuevas"
        )
        print(f"  con nodo, dificultad, explicacion, figura o texto: {len(difieren_meta)}")
        print(f"  nodos con subject equivocado:             {len(nodos_mal)} {nodos_mal}")
        print(f"  nodos con nombre, eje o tier distinto:    {len(nodos_ficha)} "
              f"{[c for c, _, _ in nodos_ficha]}")
        print(f"  nodos que ya no estan en seed_data:       {len(nodos_sobran)} "
              f"{[c for _, c in nodos_sobran]}")
        print(f"  textos que ya no estan en seed_data:      {len(textos_sobran)}")
        print(f"  faltan por insertar (las pone seed.py):   {len(faltan)}")

        if not aplicar:
            print("\n(solo informe; para ejecutar agrega --aplicar)")
            return

        # --- respaldo de TODO lo que se va a borrar -------------------------
        borrar_preguntas = [q[0] for q in sobran]
        borrar_alts = [aid for d in difieren_alt for aid in d[3]]
        ids_nodos_sobran = [nid for nid, _ in nodos_sobran]

        cur.execute(
            """select q.id, s.code, q.difficulty::text, q.stem, q.explanation
                 from questions q join skill_nodes s on s.id = q.skill_node_id
                where q.id = any(%s)""",
            (borrar_preguntas,),
        )
        resp = {
            "fecha": datetime.datetime.now(tz=datetime.UTC).isoformat(),
            "motivo": "borradas al sincronizar la base con seed_data.py",
            "preguntas": [
                dict(
                    zip(
                        ["id", "nodo", "dificultad", "stem", "explicacion"],
                        r,
                        strict=True,
                    )
                )
                for r in cur.fetchall()
            ],
        }
        for t in ("alternatives", "exam_answers", "exam_attempt_questions",
                  "practice_answers"):
            cur.execute(
                f"select * from {t} where question_id = any(%s)", (borrar_preguntas,)
            )
            cols = [d[0] for d in cur.description]
            resp[t] = [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]
        # Las alternativas reemplazadas van aparte: su pregunta NO se borra.
        cur.execute("select * from alternatives where id = any(%s)", (borrar_alts,))
        cols = [d[0] for d in cur.description]
        resp["alternativas_reemplazadas"] = [
            dict(zip(cols, r, strict=True)) for r in cur.fetchall()
        ]
        cur.execute("select * from skill_nodes where id = any(%s)", (ids_nodos_sobran,))
        cols = [d[0] for d in cur.description]
        resp["nodos_borrados"] = [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]
        cur.execute(
            "select * from user_skill_progress where skill_node_id = any(%s)",
            (ids_nodos_sobran,),
        )
        cols = [d[0] for d in cur.description]
        resp["progreso_de_nodos_borrados"] = [
            dict(zip(cols, r, strict=True)) for r in cur.fetchall()
        ]

        carpeta = Path(
            os.environ.get("PAES_BACKUP_DIR", Path.home() / "backups-1000paes")
        )
        carpeta.mkdir(parents=True, exist_ok=True)
        marca = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d-%H%M")
        ruta = carpeta / f"sincronizacion-{marca}.json"
        with ruta.open("w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=1, default=str)
        print(f"\nrespaldo: {ruta}")

        # --- correcciones en su lugar (nada desaparece) ---------------------
        for cod, _, nuevo in nodos_mal:
            cur.execute("update skill_nodes set subject=%s where code=%s", (nuevo, cod))
            print(f"  nodo {cod} -> subject {nuevo}")

        for cod, (nombre, eje, tier), viejo in nodos_ficha:
            cur.execute(
                "update skill_nodes set name=%s, axis=%s, tier=%s, display_order=%s"
                " where code=%s",
                (nombre, eje.upper(), tier, tier, cod),
            )
            print(f"  nodo {cod}: {viejo} -> {(nombre, eje, tier)}")

        for _qid, _stem, corregir, borrar, insertar in difieren_alt:
            for aid, es_correcta, justificacion in corregir:
                cur.execute(
                    "update alternatives set is_correct=%s, "
                    "distractor_justification=%s where id=%s",
                    (es_correcta, justificacion, aid),
                )
        if borrar_alts:
            # Una respuesta ya rendida puede apuntar a la alternativa que se va.
            # La respuesta se conserva (con su tiempo y su marca) y queda sin
            # seleccion, que es lo que de verdad pasa: lo que eligio ya no
            # existe. Antes se borraba la fila entera.
            cur.execute(
                "update exam_answers set selected_alternative_id=null "
                "where selected_alternative_id = any(%s)",
                (borrar_alts,),
            )
            if cur.rowcount:
                print(f"  respuestas que apuntaban a una alternativa retirada: "
                      f"{cur.rowcount} (se conservan, sin seleccion)")
            cur.execute("delete from alternatives where id = any(%s)", (borrar_alts,))
            print(f"  alternativas reemplazadas: {cur.rowcount}")
        for qid, _stem, _corregir, _borrar, insertar in difieren_alt:
            for label, texto, es_correcta, justificacion in insertar:
                cur.execute(
                    "insert into alternatives (question_id, label, text, is_correct,"
                    " distractor_justification) values (%s,%s,%s,%s,%s)",
                    (qid, label, texto, es_correcta, justificacion),
                )
        print(
            f"  {len(difieren_alt)} preguntas reparadas sin perder su id "
            f"({alt_corregidas} corregidas, {alt_nuevas} nuevas)"
        )

        for qid, objetivo, *_ in difieren_meta:
            cur.execute(
                """update questions
                      set difficulty=%s,
                          explanation=%s,
                          image_url=%s,
                          skill_node_id=(select id from skill_nodes where code=%s),
                          passage_id=(select id from reading_passages
                                       where title=%s)
                    where id=%s""",
                (
                    objetivo["dificultad"],
                    objetivo["explicacion"],
                    objetivo["imagen"],
                    objetivo["nodo"],
                    objetivo["texto_base"],
                    qid,
                ),
            )
        print(f"  {len(difieren_meta)} preguntas corregidas en nodo, dificultad, "
              "explicacion, figura o texto base")

        # --- borrados de verdad ---------------------------------------------
        if borrar_preguntas:
            for t in ("exam_answers", "exam_attempt_questions", "practice_answers",
                      "alternatives"):
                cur.execute(
                    f"delete from {t} where question_id = any(%s)", (borrar_preguntas,)
                )
                print(f"  {t}: {cur.rowcount} filas borradas")
            cur.execute("delete from questions where id = any(%s)", (borrar_preguntas,))
            print(f"  questions: {cur.rowcount} borradas")

        # Los textos van DESPUES de las preguntas: mientras exista una pregunta
        # apuntando al texto, la clave foranea impide borrarlo.
        if textos_sobran:
            ids = [i for i, _ in textos_sobran]
            cur.execute("delete from questions where passage_id = any(%s)", (ids,))
            if cur.rowcount:
                print(f"  questions huerfanas de esos textos: {cur.rowcount}")
            cur.execute("delete from reading_passages where id = any(%s)", (ids,))
            print(f"  reading_passages: {cur.rowcount} borrados")

        # Y los nodos al final, por la misma razon: primero hay que haber
        # movido sus preguntas al nodo que las hereda (eso lo hizo el bloque de
        # nodo/dificultad de mas arriba). Si todavia cuelga alguna, es que
        # seed_data no dice donde va: se aborta en vez de arrastrarla.
        if ids_nodos_sobran:
            cur.execute(
                "select count(*) from questions where skill_node_id = any(%s)",
                (ids_nodos_sobran,),
            )
            colgando = cur.fetchone()[0]
            if colgando:
                raise SystemExit(
                    f"abortado: {colgando} preguntas siguen en un nodo que ya no "
                    "esta en seed_data. Asignales un nodo vivo en seed_data.py "
                    "antes de sincronizar."
                )
            for t, col in (
                ("lessons", "skill_node_id"),
                ("practice_answers", "skill_node_id"),
                ("user_skill_progress", "skill_node_id"),
                ("skill_prerequisites", "skill_node_id"),
                ("skill_prerequisites", "prerequisite_id"),
            ):
                cur.execute(
                    f"delete from {t} where {col} = any(%s)", (ids_nodos_sobran,)
                )
                if cur.rowcount:
                    print(f"  {t}.{col}: {cur.rowcount} filas borradas")
            cur.execute("delete from skill_nodes where id = any(%s)", (ids_nodos_sobran,))
            print(f"  skill_nodes: {cur.rowcount} borrados "
                  f"({', '.join(c for _, c in nodos_sobran)})")

        c.commit()
        print("commit OK. La base quedo igual a seed_data.py.")


if __name__ == "__main__":
    main()
