"""Carga SKILL_NODES y QUESTIONS (seed_data.py) a la base de datos.

Idempotente: si un SkillNode.code o un Question.stem ya existen, se
omiten. El orden de las alternativas se mezcla con una semilla fija
(determinística) para no dejar siempre la correcta en la posición A.

Uso:
    uv run python scripts/seed.py
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import select

import paes_api.all_models  # noqa: F401 — registra todos los modelos en Base.metadata
from paes_api.core.database import SessionLocal, engine
from paes_api.core.security import hash_password
from paes_api.modules.content.models import (
    Alternative,
    Difficulty,
    Lesson,
    Question,
    ReadingPassage,
)
from paes_api.modules.goals.models import Carrera
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode, Subject
from paes_api.modules.users.models import User
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
from paes_api.shared.base import Base

DEMO_EMAIL = "demo@paes-m1.cl"
DEMO_PASSWORD = "demo1234"

LABELS = ["A", "B", "C", "D"]
RNG = random.Random(42)


def seed_skill_nodes(db) -> dict[str, SkillNode]:
    all_nodes = (
        [(*n, Subject.M1) for n in SKILL_NODES]
        + [(*n, Subject.M2) for n in SKILL_NODES_M2]
        + [(*n, Subject.LECTORA) for n in SKILL_NODES_LECTORA]
        + [(*n, Subject.CIENCIAS) for n in SKILL_NODES_CIENCIAS]
        + [(*n, Subject.HISTORIA) for n in SKILL_NODES_HISTORIA]
    )

    by_code: dict[str, SkillNode] = {}
    for code, name, axis, tier, _prereqs, subject in all_nodes:
        existing = db.execute(
            select(SkillNode).where(SkillNode.code == code)
        ).scalar_one_or_none()
        if existing:
            by_code[code] = existing
            continue
        node = SkillNode(
            code=code,
            name=name,
            axis=SkillAxis(axis),
            subject=subject,
            tier=tier,
            unlock_threshold=0.75,
            display_order=tier,
        )
        db.add(node)
        by_code[code] = node
    db.flush()

    for code, *_rest, prereq_codes, _subject in all_nodes:
        node = by_code[code]
        node.prerequisites = [by_code[p] for p in prereq_codes]
    db.commit()
    print(f"skill_nodes: {len(by_code)} nodos (creados o ya existentes)")
    return by_code


def seed_passages(db) -> dict[str, ReadingPassage]:
    """Siembra los textos de Competencia Lectora. Idempotente por título."""
    by_key: dict[str, ReadingPassage] = {}
    creados = 0
    actualizados = 0
    for p in PASSAGES + PASSAGES_HISTORIA:
        existing = db.execute(
            select(ReadingPassage).where(ReadingPassage.title == p["title"])
        ).scalar_one_or_none()
        if existing:
            # El texto sí se actualiza (a diferencia del enunciado de una
            # pregunta, que identifica el registro): corregir una errata o
            # mejorar el formato de una tabla no debe obligar a borrar el
            # pasaje y perder las preguntas que cuelgan de él.
            cambios = (
                existing.body != p["body"]
                or existing.kind != p["kind"]
                or existing.source_note != p.get("source_note")
            )
            if cambios:
                existing.body = p["body"]
                existing.kind = p["kind"]
                existing.source_note = p.get("source_note")
                actualizados += 1
            by_key[p["key"]] = existing
            continue
        passage = ReadingPassage(
            title=p["title"],
            body=p["body"],
            kind=p["kind"],
            source_note=p.get("source_note"),
        )
        db.add(passage)
        by_key[p["key"]] = passage
        creados += 1
    db.flush()
    print(
        f"reading_passages: {creados} nuevos, {actualizados} actualizados "
        f"(de {len(PASSAGES) + len(PASSAGES_HISTORIA)} definidos)"
    )
    return by_key


def seed_questions(
    db,
    nodes_by_code: dict[str, SkillNode],
    passages_by_key: dict[str, ReadingPassage] | None = None,
) -> None:
    passages_by_key = passages_by_key or {}
    TODAS_LAS_PREGUNTAS = (
        QUESTIONS + QUESTIONS_LECTORA + QUESTIONS_CIENCIAS + QUESTIONS_HISTORIA
    )
    created = 0
    updated = 0
    for q in TODAS_LAS_PREGUNTAS:
        exists = db.execute(
            select(Question).where(Question.stem == q["stem"])
        ).scalar_one_or_none()
        if exists:
            # La pregunta ya está, pero su explicación puede haber cambiado (o
            # no existir, si se sembró antes de que hubiera columna). Se
            # actualiza sin tocar las alternativas, para no invalidar los
            # intentos que ya apuntan a ellas.
            if exists.explanation != q["explanation"]:
                exists.explanation = q["explanation"]
                updated += 1
            continue

        question = Question(
            skill_node_id=nodes_by_code[q["skill_node"]].id,
            difficulty=Difficulty(q["difficulty"]),
            stem=q["stem"],
            explanation=q["explanation"],
        )
        clave = q.get("passage")
        if clave:
            question.passage = passages_by_key[clave]
        db.add(question)
        db.flush()

        shuffled = q["alternatives"][:]
        RNG.shuffle(shuffled)
        for label, alt in zip(LABELS, shuffled):
            db.add(
                Alternative(
                    question_id=question.id,
                    label=label,
                    text=alt["text"],
                    is_correct=alt["is_correct"],
                    distractor_justification=alt["justification"],
                )
            )
        created += 1
    db.commit()
    print(
        f"questions: {created} nuevas insertadas, {updated} explicaciones actualizadas "
        f"(de {len(TODAS_LAS_PREGUNTAS)} definidas)"
    )


def seed_lessons(db, nodes_by_code: dict[str, SkillNode]) -> None:
    """Siembra la teoría de cada nodo. Idempotente por nodo, y SÍ actualiza.

    A diferencia de una pregunta —cuyo enunciado identifica el registro—, una
    lección se corrige: mejorar una explicación o arreglar una errata no puede
    obligar a borrar el nodo.
    """
    creadas = 0
    actualizadas = 0
    for code, datos in LESSONS.items():
        node = nodes_by_code.get(code)
        if node is None:
            print(f"  aviso: lección de un nodo que no existe ({code}), se omite")
            continue

        existente = db.execute(
            select(Lesson).where(Lesson.skill_node_id == node.id)
        ).scalar_one_or_none()

        if existente is None:
            db.add(
                Lesson(
                    skill_node_id=node.id,
                    intro=datos["intro"],
                    theory=datos["theory"],
                    example_statement=datos["example_statement"],
                    example_steps=datos["example_steps"],
                    common_error=datos.get("common_error"),
                )
            )
            creadas += 1
            continue

        cambios = (
            existente.intro != datos["intro"]
            or existente.theory != datos["theory"]
            or existente.example_statement != datos["example_statement"]
            or existente.example_steps != datos["example_steps"]
            or existente.common_error != datos.get("common_error")
        )
        if cambios:
            existente.intro = datos["intro"]
            existente.theory = datos["theory"]
            existente.example_statement = datos["example_statement"]
            existente.example_steps = datos["example_steps"]
            existente.common_error = datos.get("common_error")
            actualizadas += 1

    db.commit()
    print(
        f"lessons: {creadas} nuevas, {actualizadas} actualizadas "
        f"(de {len(LESSONS)} definidas)"
    )


def seed_carreras(db) -> None:
    """Carga las ponderaciones oficiales del proceso vigente.

    El archivo lo genera `scripts/extraer_carreras.py` desde el PDF del DEMRE y
    solo contiene carreras cuyas ponderaciones suman 100. Se actualiza en vez de
    duplicar: cada proceso cambia los pesos y una carrera tiene que poder
    corregirse sin perder las metas que apuntan a ella.
    """
    import json

    ruta = Path(__file__).resolve().parents[1] / "src/paes_api/data/carreras_2026.json"
    if not ruta.exists():
        print("carreras: falta el archivo de datos, se omite")
        return

    datos = json.loads(ruta.read_text(encoding="utf-8"))
    existentes = {
        c.codigo: c for c in db.execute(select(Carrera)).scalars().all()
    }

    creadas = actualizadas = 0
    for fila in datos["carreras"]:
        valores = {
            "universidad": fila["universidad"],
            "nombre": fila["carrera"],
            "sede": fila["sede"],
            "nem": fila.get("nem"),
            "ranking": fila.get("ranking"),
            "lectora": fila.get("lectora"),
            "m1": fila.get("m1"),
            "historia": fila.get("historia"),
            "ciencias": fila.get("ciencias"),
            "m2": fila.get("m2"),
            "prueba_especial": fila.get("prueba_especial"),
            "electivo_alternativo": fila.get("electivo_alternativo", False),
            "ponderado_min": fila.get("ponderado_min"),
            "promedio_min": fila.get("promedio_min"),
            "vacantes": fila.get("vacantes"),
            "proceso": datos["proceso"],
            "fuente": datos["fuente"],
        }
        actual = existentes.get(fila["codigo"])
        if actual is None:
            db.add(Carrera(codigo=fila["codigo"], **valores))
            creadas += 1
        elif any(getattr(actual, k) != v for k, v in valores.items()):
            for k, v in valores.items():
                setattr(actual, k, v)
            actualizadas += 1

    db.commit()
    print(
        f"carreras: {creadas} nuevas, {actualizadas} actualizadas "
        f"(proceso {datos['proceso']}, {len(datos['carreras'])} en el archivo)"
    )


def seed_codigos(db) -> None:
    """Códigos de ejemplo para poder probar el canje sin pasarela.

    Son de prueba y con tope bajo a propósito: un código de demostración con
    usos ilimitados en producción es plan Pro gratis para quien lo adivine.
    """
    from datetime import UTC, datetime, timedelta

    from paes_api.modules.billing.models import Plan, PromoCode

    ejemplos = [
        {
            "codigo": "PRUEBA-PRO",
            "plan": Plan.PRO,
            "dias": 30,
            "usos_maximos": 20,
            "descripcion": "Código de prueba interna, 30 días de Pro",
            "vence_el": datetime.now(UTC) + timedelta(days=90),
        },
    ]

    creados = 0
    for datos in ejemplos:
        existe = db.execute(
            select(PromoCode).where(PromoCode.codigo == datos["codigo"])
        ).scalar_one_or_none()
        if existe is None:
            db.add(PromoCode(**datos))
            creados += 1
    db.commit()
    print(f"promo_codes: {creados} nuevos (de {len(ejemplos)} definidos)")


def seed_demo_user(db) -> None:
    existing = db.execute(select(User).where(User.email == DEMO_EMAIL)).scalar_one_or_none()
    if existing:
        if not existing.hashed_password:
            existing.hashed_password = hash_password(DEMO_PASSWORD)
            db.commit()
            print(f"demo user: password rellenada ({DEMO_EMAIL} / {DEMO_PASSWORD})")
        else:
            print(f"demo user: ya existe ({DEMO_EMAIL})")
        return
    db.add(
        User(
            email=DEMO_EMAIL,
            hashed_password=hash_password(DEMO_PASSWORD),
            name="Estudiante Demo",
        )
    )
    db.commit()
    print(f"demo user: creado ({DEMO_EMAIL} / {DEMO_PASSWORD})")


def main() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        nodes = seed_skill_nodes(db)
        passages = seed_passages(db)
        seed_questions(db, nodes, passages)
        seed_lessons(db, nodes)
        seed_carreras(db)
        seed_codigos(db)
        seed_demo_user(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
