"""leads: correos de gente sin cuenta

Revision ID: e4a91b70c5d2
Revises: c8f21d0a6b13
Create Date: 2026-08-20

Tabla nueva, no toca nada existente. Guarda el correo de quien probó la demo y
todavía no se registró, que hasta ahora se perdía entero al cerrar la pestaña.

El correo es único: dejarlo dos veces no crea dos filas. Deliberadamente NO hay
IP ni nombre — para escribirle a alguien basta su correo.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e4a91b70c5d2"
down_revision: str | Sequence[str] | None = "c8f21d0a6b13"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_leads_email"), "leads", ["email"], unique=True)
    # Se consulta "cuántos correos entraron esta semana": sin índice, cada
    # lectura del panel recorre la tabla completa.
    op.create_index(op.f("ix_leads_created_at"), "leads", ["created_at"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_leads_created_at"), table_name="leads")
    op.drop_index(op.f("ix_leads_email"), table_name="leads")
    op.drop_table("leads")
