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
    Question,
    ReadingPassage,
)
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode, Subject
from paes_api.modules.users.models import User
from paes_api.seed_data import (
    PASSAGES,
    QUESTIONS,
    QUESTIONS_LECTORA,
    SKILL_NODES,
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
    for p in PASSAGES:
        existing = db.execute(
            select(ReadingPassage).where(ReadingPassage.title == p["title"])
        ).scalar_one_or_none()
        if existing:
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
    print(f"reading_passages: {creados} nuevos (de {len(PASSAGES)} definidos)")
    return by_key


def seed_questions(
    db,
    nodes_by_code: dict[str, SkillNode],
    passages_by_key: dict[str, ReadingPassage] | None = None,
) -> None:
    passages_by_key = passages_by_key or {}
    TODAS_LAS_PREGUNTAS = QUESTIONS + QUESTIONS_LECTORA
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
        f"(de {len(QUESTIONS)} definidas)"
    )


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
        seed_demo_user(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
