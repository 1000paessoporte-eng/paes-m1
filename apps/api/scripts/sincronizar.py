"""Deja la base igual a seed_data.py. seed.py solo INSERTA; esto reconcilia.

`scripts/seed.py` salta cualquier pregunta cuyo enunciado ya exista, y esa
regla —la que lo hace idempotente— tiene un costo: no publica nada de lo que
cambia SIN cambiar el enunciado. Corriendo solo seed.py no llegan a produccion
los cambios de dificultad, ni los distractores corregidos, ni el cambio de
prueba de un nodo (M1 a M2). Y peor: cuando una pregunta se reescribe, la
version vieja queda VIVA, porque la nueva tiene otro enunciado y entra como si
fuera adicional.

Este script borra lo que ya no esta en seed_data, rehace las preguntas cuyas
alternativas cambiaron y corrige nodo y dificultad. Lo que falta lo inserta
seed.py, asi que la secuencia completa para publicar es:

    seed.py  ->  sincronizar.py --aplicar  ->  seed.py

El primer seed crea los nodos nuevos —sin ellos el sync no puede reasignar
preguntas a un nodo que todavia no existe— e inserta lo nuevo; el sync limpia y
corrige; el ultimo seed repone las preguntas que el sync borro por tener
alternativas distintas.

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
import psycopg

from paes_api.seed_data import (
    PASSAGES,
    PASSAGES_HISTORIA,
    QUESTIONS,
    QUESTIONS_LECTORA,
    SKILL_NODES,
    SKILL_NODES_M2,
)

APLICAR = '--aplicar' in sys.argv
url = os.environ['DATABASE_URL'].replace('postgresql+psycopg://', 'postgresql://')

M1 = {n[0] for n in SKILL_NODES}
M2 = {n[0] for n in SKILL_NODES_M2}
SUBJECT = {c: 'M1' for c in M1} | {c: 'M2' for c in M2}

# estado deseado, tomado del repo
deseado = {}
# Lectora entra en la misma comparacion: sus preguntas tienen la misma forma
# y su banco tambien cambia.
for q in QUESTIONS + QUESTIONS_LECTORA:
    alts = tuple(sorted((a['text'], a['is_correct']) for a in q['alternatives']))
    deseado[q['stem']] = (q['skill_node'], q['difficulty'].upper(), alts)

with psycopg.connect(url, connect_timeout=30) as c, c.cursor() as cur:
    cur.execute("""select q.id, q.stem, s.code, q.difficulty::text
                   from questions q join skill_nodes s on s.id = q.skill_node_id
                   where s.subject in ('M1','M2','LECTORA')""")
    filas = cur.fetchall()
    cur.execute("select question_id, text, is_correct from alternatives")
    porq = {}
    for qid, txt, ok in cur.fetchall():
        porq.setdefault(qid, []).append((txt, ok))

    sobran, difieren_alt, difieren_meta = [], [], []
    for qid, stem, code, dif in filas:
        if stem not in deseado:
            sobran.append((qid, code, stem))
            continue
        code_ok, dif_ok, alts_ok = deseado[stem]
        if tuple(sorted(porq.get(qid, []))) != alts_ok:
            difieren_alt.append((qid, code, stem))
        elif (code, dif) != (code_ok, dif_ok):
            difieren_meta.append((qid, code, dif, code_ok, dif_ok, stem))

    # nodos cuyo subject cambio (prob_combinatoria paso de M1 a M2)
    cur.execute("select code, subject::text from skill_nodes")
    nodos_mal = [(cod, sub, SUBJECT[cod]) for cod, sub in cur.fetchall()
                 if cod in SUBJECT and sub != SUBJECT[cod]]

    print(f"preguntas de matematica y lectora en produccion: {len(filas)}")
    print(f"  sobran (ya no estan en seed_data):        {len(sobran)}")
    print(f"  con alternativas distintas (se rehacen):  {len(difieren_alt)}")
    print(f"  solo nodo o dificultad distinta:          {len(difieren_meta)}")
    print(f"  nodos con subject equivocado:             {len(nodos_mal)} {nodos_mal}")
    # Los textos se identifican por titulo, que es como los busca seed.py.
    titulos_ok = {p["title"] for p in PASSAGES + PASSAGES_HISTORIA}
    cur.execute("select id, title from reading_passages")
    textos_sobran = [(i, t) for i, t in cur.fetchall() if t not in titulos_ok]
    print(f"  textos que ya no estan en seed_data:      {len(textos_sobran)}")

    faltan = set(deseado) - {f[1] for f in filas}
    print(f"  faltan por insertar:                      {len(faltan)}")

    if not APLICAR:
        print("\n(solo informe; para ejecutar agrega --aplicar)")
        sys.exit(0)

    borrar = [q[0] for q in sobran] + [q[0] for q in difieren_alt]
    # respaldo antes de tocar nada
    cur.execute("""select q.id, s.code, q.difficulty::text, q.stem, q.explanation
                   from questions q join skill_nodes s on s.id = q.skill_node_id
                   where q.id = any(%s)""", (borrar,))
    resp = {"fecha": datetime.datetime.now(tz=datetime.UTC).isoformat(),
            "motivo": "borradas al sincronizar la base con seed_data.py",
            "preguntas": [dict(zip(['id', 'nodo', 'dificultad', 'stem', 'explicacion'], r, strict=True))
                          for r in cur.fetchall()]}
    for t in ('alternatives', 'exam_answers', 'exam_attempt_questions', 'practice_answers'):
        cur.execute(f"select * from {t} where question_id = any(%s)", (borrar,))
        cols = [d[0] for d in cur.description]
        resp[t] = [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]
    carpeta = Path(os.environ.get("PAES_BACKUP_DIR", Path.home() / "backups-1000paes"))
    carpeta.mkdir(parents=True, exist_ok=True)
    marca = datetime.datetime.now(tz=datetime.UTC).strftime("%Y-%m-%d-%H%M")
    ruta = carpeta / f"sincronizacion-{marca}.json"
    with ruta.open('w', encoding='utf-8') as f:
        json.dump(resp, f, ensure_ascii=False, indent=1, default=str)
    print(f"\nrespaldo: {ruta}")

    for cod, _, nuevo in nodos_mal:
        cur.execute("update skill_nodes set subject=%s where code=%s", (nuevo, cod))
        print(f"  nodo {cod} -> subject {nuevo}")

    for t in ('exam_answers', 'exam_attempt_questions', 'practice_answers', 'alternatives'):
        cur.execute(f"delete from {t} where question_id = any(%s)", (borrar,))
        print(f"  {t}: {cur.rowcount} filas borradas")
    cur.execute("delete from questions where id = any(%s)", (borrar,))
    print(f"  questions: {cur.rowcount} borradas")

    # Los textos van DESPUES de las preguntas: mientras exista una pregunta
    # apuntando al texto, la clave foranea impide borrarlo.
    if textos_sobran:
        ids = [i for i, _ in textos_sobran]
        cur.execute(
            "delete from questions where passage_id = any(%s)", (ids,)
        )
        if cur.rowcount:
            print(f"  questions huerfanas de esos textos: {cur.rowcount}")
        cur.execute("delete from reading_passages where id = any(%s)", (ids,))
        print(f"  reading_passages: {cur.rowcount} borrados")

    for qid, _, _, code_ok, dif_ok, _ in difieren_meta:
        cur.execute("""update questions set difficulty=%s,
                       skill_node_id=(select id from skill_nodes where code=%s)
                       where id=%s""", (dif_ok, code_ok, qid))
    print(f"  {len(difieren_meta)} preguntas corregidas en nodo/dificultad")

    c.commit()
    print("commit OK. Ahora corre scripts/seed.py para insertar lo que falta.")
