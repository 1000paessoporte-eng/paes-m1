"""Reportes de preguntas del banco

Un alumno que se topa con una pregunta mal planteada no tenía dónde decirlo.
`verificar_banco.py` recalcula la aritmética y comprueba la estructura, pero no
ve un enunciado ambiguo ni una clave apuntando a la alternativa equivocada; eso
lo ve quien está respondiendo.

Una fila por aviso, no un contador agrupado como en `errores_cliente`: acá el
comentario de cada persona es el dato que permite decidir.

Revision ID: b7d4e9f1a2c3
Revises: c8f1a4d92e30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b7d4e9f1a2c3"
down_revision: str | None = "c8f1a4d92e30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reportes_pregunta",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("motivo", sa.String(length=30), nullable=False),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("contexto", sa.String(length=20), nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("revisado_en", sa.DateTime(timezone=True), nullable=True),
        # Si la pregunta se borra del banco, el aviso se va con ella: sin la
        # pregunta no queda nada que revisar. La cuenta, en cambio, se conserva
        # como anónima: el aviso sigue siendo válido aunque quien lo dio se
        # haya borrado.
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reportes_pregunta_question_id"),
        "reportes_pregunta",
        ["question_id"],
    )
    op.create_index(
        op.f("ix_reportes_pregunta_user_id"), "reportes_pregunta", ["user_id"]
    )
    op.create_index(
        op.f("ix_reportes_pregunta_creado_en"), "reportes_pregunta", ["creado_en"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reportes_pregunta_creado_en"), table_name="reportes_pregunta")
    op.drop_index(op.f("ix_reportes_pregunta_user_id"), table_name="reportes_pregunta")
    op.drop_index(
        op.f("ix_reportes_pregunta_question_id"), table_name="reportes_pregunta"
    )
    op.drop_table("reportes_pregunta")
