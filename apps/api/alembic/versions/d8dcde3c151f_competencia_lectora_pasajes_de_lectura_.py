"""competencia lectora: pasajes de lectura y ejes de habilidad

Revision ID: d8dcde3c151f
Revises: 5aed85013803
Create Date: 2026-08-14 22:12:01.557033

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd8dcde3c151f'
down_revision: str | Sequence[str] | None = '5aed85013803'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Los enums de subject y skillaxis son nativos de Postgres. ALTER TYPE ADD
    # VALUE no puede correr dentro de la transacción que además USA el valor
    # nuevo, así que va en un bloque con autocommit propio.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE subject ADD VALUE IF NOT EXISTS 'LECTORA'")
        op.execute("ALTER TYPE skillaxis ADD VALUE IF NOT EXISTS 'LOCALIZAR'")
        op.execute("ALTER TYPE skillaxis ADD VALUE IF NOT EXISTS 'INTERPRETAR'")
        op.execute("ALTER TYPE skillaxis ADD VALUE IF NOT EXISTS 'EVALUAR'")

    op.create_table(
        "reading_passages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False, server_default="no_literario"),
        sa.Column("source_note", sa.String(length=300), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("questions", sa.Column("passage_id", sa.Integer(), nullable=True))
    op.create_index("ix_questions_passage_id", "questions", ["passage_id"])
    op.create_foreign_key(
        "fk_questions_passage_id", "questions", "reading_passages", ["passage_id"], ["id"]
    )


def downgrade() -> None:
    # Los valores agregados a un enum de Postgres no se pueden quitar sin
    # recrear el tipo. Como son aditivos y nada los usa tras borrar los datos,
    # se dejan: revertir la tabla y la columna alcanza.
    op.drop_constraint("fk_questions_passage_id", "questions", type_="foreignkey")
    op.drop_index("ix_questions_passage_id", table_name="questions")
    op.drop_column("questions", "passage_id")
    op.drop_table("reading_passages")
