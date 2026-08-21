"""Quita repaso_items: el repaso deja de ser un módulo aparte

La señal que servía --"esta pregunta ya la fallaste"-- pasa a mostrarse dentro
del ensayo, y para eso no hace falta guardar estado: se deduce de las
respuestas que ya están en exam_answers y practice_answers.

El downgrade recrea la tabla vacía. Las filas de estado (peldaño y próxima
fecha) no se pueden reconstruir, y no importa: eran un derivado de las
respuestas, que siguen intactas.

Revision ID: f1a7c30b94e6
Revises: d5f8a02c9b71
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f1a7c30b94e6"
down_revision: str | None = "d5f8a02c9b71"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(op.f("ix_repaso_items_proxima_fecha"), table_name="repaso_items")
    op.drop_index(op.f("ix_repaso_items_question_id"), table_name="repaso_items")
    op.drop_index(op.f("ix_repaso_items_user_id"), table_name="repaso_items")
    op.drop_table("repaso_items")


def downgrade() -> None:
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
        sa.UniqueConstraint("user_id", "question_id", name="uq_repaso_usuario_pregunta"),
    )
    op.create_index(op.f("ix_repaso_items_user_id"), "repaso_items", ["user_id"])
    op.create_index(op.f("ix_repaso_items_question_id"), "repaso_items", ["question_id"])
    op.create_index(op.f("ix_repaso_items_proxima_fecha"), "repaso_items", ["proxima_fecha"])
