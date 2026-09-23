"""solicitudes de cotizacion de colegios

Tabla nueva: no toca nada de lo que ya existe, así que no tiene el riesgo de
una columna agregada a una tabla viva.

OJO si se mergea junto con el login de Microsoft (PR #203): esa rama trae otra
migración que también cuelga de `c3a8b5d21e47`, y dos cabezas dejan a alembic
sin saber cuál aplicar. La segunda que se mergee tiene que reapuntar su
`down_revision` a la primera.

Revision ID: 66e1ba677d86
Revises: c3a8b5d21e47
Create Date: 2026-09-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "66e1ba677d86"
down_revision: str | None = "c3a8b5d21e47"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "solicitudes_colegio",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("establecimiento", sa.String(length=160), nullable=False),
        sa.Column("contacto", sa.String(length=120), nullable=False),
        sa.Column("cargo", sa.String(length=60), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("telefono", sa.String(length=40), nullable=True),
        sa.Column("comuna", sa.String(length=80), nullable=True),
        sa.Column("alumnos", sa.Integer(), nullable=False),
        sa.Column("mensaje", sa.Text(), nullable=True),
        sa.Column(
            "atendida", sa.Boolean(), server_default="false", nullable=False
        ),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_solicitudes_colegio_email"), "solicitudes_colegio", ["email"]
    )
    # Por fecha: el panel las lista de la más nueva a la más vieja.
    op.create_index(
        op.f("ix_solicitudes_colegio_creado_en"), "solicitudes_colegio", ["creado_en"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_solicitudes_colegio_creado_en"), table_name="solicitudes_colegio")
    op.drop_index(op.f("ix_solicitudes_colegio_email"), table_name="solicitudes_colegio")
    op.drop_table("solicitudes_colegio")
