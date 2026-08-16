"""ciencias: ejes de biologia fisica y quimica

Revision ID: 4d3c6b5b94d3
Revises: d8dcde3c151f
Create Date: 2026-08-14 22:34:58.958578

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4d3c6b5b94d3'
down_revision: str | Sequence[str] | None = 'd8dcde3c151f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Solo valores de enum: la estructura de Ciencias (ejes por disciplina) cabe
    # en el modelo que ya existe, igual que pasó con Competencia Lectora.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE subject ADD VALUE IF NOT EXISTS 'CIENCIAS'")
        op.execute("ALTER TYPE skillaxis ADD VALUE IF NOT EXISTS 'BIOLOGIA'")
        op.execute("ALTER TYPE skillaxis ADD VALUE IF NOT EXISTS 'FISICA'")
        op.execute("ALTER TYPE skillaxis ADD VALUE IF NOT EXISTS 'QUIMICA'")


def downgrade() -> None:
    # Postgres no permite quitar valores de un enum sin recrear el tipo. Son
    # aditivos: basta con que nada los use.
    pass
