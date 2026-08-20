"""visitas: campaña de origen (UTM)

Revision ID: b7c2e9f14a30
Revises: e4a91b70c5d2
Create Date: 2026-08-20

Cuatro columnas nulables sobre page_views. Sin backfill: las visitas anteriores
quedan en NULL, que es la verdad — de esas no se sabe qué campaña las trajo, y
adivinarlo sería inventar datos.

Solo se indexa utm_campaign, que es por donde agrupa el panel. Las otras tres
se leen dentro del grupo ya acotado.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b7c2e9f14a30"
down_revision: str | Sequence[str] | None = "e4a91b70c5d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    for columna in ("utm_source", "utm_medium", "utm_campaign", "utm_content"):
        op.add_column("page_views", sa.Column(columna, sa.String(length=100), nullable=True))
    op.create_index(op.f("ix_page_views_utm_campaign"), "page_views", ["utm_campaign"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_page_views_utm_campaign"), table_name="page_views")
    for columna in ("utm_content", "utm_campaign", "utm_medium", "utm_source"):
        op.drop_column("page_views", columna)
