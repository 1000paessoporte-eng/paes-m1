"""historia: ejes de historia ciudadania y economia

Revision ID: ee1cd1ac1478
Revises: 4d3c6b5b94d3
Create Date: 2026-08-14 23:02:14.460236

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ee1cd1ac1478'
down_revision: str | Sequence[str] | None = '4d3c6b5b94d3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE subject ADD VALUE IF NOT EXISTS 'HISTORIA'")
        op.execute("ALTER TYPE skillaxis ADD VALUE IF NOT EXISTS 'HISTORIA'")
        op.execute("ALTER TYPE skillaxis ADD VALUE IF NOT EXISTS 'CIUDADANIA'")
        op.execute("ALTER TYPE skillaxis ADD VALUE IF NOT EXISTS 'ECONOMIA'")


def downgrade() -> None:
    # Postgres no permite quitar valores de un enum sin recrear el tipo.
    pass
