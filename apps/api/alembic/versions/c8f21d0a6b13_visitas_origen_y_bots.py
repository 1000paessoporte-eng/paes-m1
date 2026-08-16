"""visitas: origen y detección de bots

Revision ID: c8f21d0a6b13
Revises: b3c7e1a94f20
Create Date: 2026-08-16

Dos columnas nulables sobre page_views. Las filas existentes quedan con
referrer NULL y es_bot false: no se puede saber retroactivamente de dónde
vinieron ni si eran robots, y adivinarlo sería inventar datos. El panel las
cuenta como tráfico sin clasificar hasta que se renueven solas.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c8f21d0a6b13"
down_revision: str | Sequence[str] | None = "b3c7e1a94f20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "page_views", sa.Column("referrer", sa.String(length=120), nullable=True)
    )
    op.add_column(
        "page_views",
        sa.Column(
            "es_bot", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
    )
    # El panel agrupa por origen y filtra por es_bot en cada consulta: sin
    # índices, cada carga recorrería la tabla entera.
    op.create_index(op.f("ix_page_views_referrer"), "page_views", ["referrer"])
    op.create_index(op.f("ix_page_views_es_bot"), "page_views", ["es_bot"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_page_views_es_bot"), table_name="page_views")
    op.drop_index(op.f("ix_page_views_referrer"), table_name="page_views")
    op.drop_column("page_views", "es_bot")
    op.drop_column("page_views", "referrer")
