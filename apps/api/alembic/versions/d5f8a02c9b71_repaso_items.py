"""Repaso inteligente: la cola de preguntas falladas

La tabla guarda el ESTADO del repaso de cada pregunta, no las respuestas: esas
siguen yendo a practice_answers, para que repasar sume a la racha y a la
analítica como cualquier otra práctica.

No hace falta rellenar nada: el service crea los items la primera vez que el
alumno abre el repaso, mirando cuáles preguntas tienen su última respuesta
incorrecta. Así la cola nace llena para quien ya venía usando la plataforma sin
que esta migración tenga que recorrer el historial completo de nadie.

Revision ID: d5f8a02c9b71
Revises: c9d13e58f2a1
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d5f8a02c9b71"
down_revision: str | None = "c9d13e58f2a1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "repaso_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("nivel", sa.Integer(), server_default="0", nullable=False),
        sa.Column("proxima_fecha", sa.Date(), nullable=True),
        sa.Column("veces_vista", sa.Integer(), server_default="0", nullable=False),
        sa.Column("veces_fallada", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        # Una pregunta entra UNA vez a la cola de un alumno: dos ensayos donde
        # falló la misma pregunta la programarían dos veces.
        sa.UniqueConstraint("user_id", "question_id", name="uq_repaso_usuario_pregunta"),
    )
    op.create_index(op.f("ix_repaso_items_user_id"), "repaso_items", ["user_id"])
    op.create_index(op.f("ix_repaso_items_question_id"), "repaso_items", ["question_id"])
    # La consulta de cada visita es "lo vencido de este usuario": el índice por
    # fecha es el que la sostiene cuando la cola crezca.
    op.create_index(op.f("ix_repaso_items_proxima_fecha"), "repaso_items", ["proxima_fecha"])


def downgrade() -> None:
    op.drop_index(op.f("ix_repaso_items_proxima_fecha"), table_name="repaso_items")
    op.drop_index(op.f("ix_repaso_items_question_id"), table_name="repaso_items")
    op.drop_index(op.f("ix_repaso_items_user_id"), table_name="repaso_items")
    op.drop_table("repaso_items")
