"""login con microsoft

Una columna nullable sobre una tabla con filas: no necesita los tres pasos de
una NOT NULL (nullable, UPDATE, NOT NULL), porque las cuentas que ya existen
se quedan en NULL, que es exactamente lo que significan — no entraron con
Microsoft.

Revision ID: 3988b90670be
Revises: c3a8b5d21e47
Create Date: 2026-09-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "3988b90670be"
down_revision: str | None = "c3a8b5d21e47"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("microsoft_sub", sa.String(length=64), nullable=True))
    # Único: dos cuentas no pueden apuntar a la misma persona de Microsoft.
    # Con índice, porque cada inicio de sesión busca por esta columna.
    op.create_index(
        op.f("ix_users_microsoft_sub"), "users", ["microsoft_sub"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_users_microsoft_sub"), table_name="users")
    op.drop_column("users", "microsoft_sub")
