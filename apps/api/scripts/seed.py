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
from paes_api.modules.content.models import Alternative, Difficulty, Question
from paes_api.modules.skill_tree.models import SkillAxis, SkillNode
from paes_api.modules.users.models import User
from paes_api.seed_data import QUESTIONS, SKILL_NODES
from paes_api.shared.base import Base

DEMO_EMAIL = "demo@paes-m1.cl"
DEMO_PASSWORD = "demo1234"

LABELS = ["A", "B", "C", "D"]
RNG = random.Random(42)


def seed_skill_nodes(db) -> dict[str, SkillNode]:
    by_code: dict[str, SkillNode] = {}
    for code, name, axis, tier, _prereqs in SKILL_NODES:
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
            tier=tier,
            unlock_threshold=0.75,
            display_order=tier,
        )
        db.add(node)
        by_code[code] = node
    db.flush()

    for code, *_rest, prereq_codes in SKILL_NODES:
        node = by_code[code]
        node.prerequisites = [by_code[p] for p in prereq_codes]
    db.commit()
    print(f"skill_nodes: {len(by_code)} nodos (creados o ya existentes)")
    return by_code


def seed_questions(db, nodes_by_code: dict[str, SkillNode]) -> None:
    created = 0
    updated = 0
    for q in QUESTIONS:
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
        seed_questions(db, nodes)
        seed_demo_user(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
