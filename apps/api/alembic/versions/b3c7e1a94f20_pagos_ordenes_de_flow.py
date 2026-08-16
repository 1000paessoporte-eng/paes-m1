"""pagos: órdenes de Flow

Revision ID: b3c7e1a94f20
Revises: f51fd8590bb7
Create Date: 2026-08-16

Tabla nueva, sin tocar ninguna existente: se puede aplicar con la API antigua
todavía corriendo, porque nada la consulta hasta que se despliegue el código
que la usa.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b3c7e1a94f20"
down_revision: str | Sequence[str] | None = "f51fd8590bb7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "pagos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("orden", sa.String(length=40), nullable=False),
        sa.Column(
            "plan",
            # El tipo `plan` ya existe: lo creó la migración de suscripciones.
            # Sin create_type=False, alembic intenta crearlo de nuevo y la
            # migración completa falla con "type plan already exists".
            postgresql.ENUM(
                "GRATIS", "PRO", "COLEGIOS", name="plan", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("dias", sa.Integer(), nullable=False),
        sa.Column("monto", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDIENTE", "PAGADO", "RECHAZADO", "ANULADO", name="pagostatus"
            ),
            nullable=False,
        ),
        sa.Column("token", sa.String(length=120), nullable=True),
        sa.Column("flow_order", sa.String(length=40), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("confirmado_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pagos_user_id"), "pagos", ["user_id"])
    # Único: es la llave con que se reconoce la orden cuando Flow responde, y
    # Flow además exige que un commerceOrder no se repita jamás.
    op.create_index(op.f("ix_pagos_orden"), "pagos", ["orden"], unique=True)
    # El webhook busca por token en cada confirmación: sin índice, cada aviso
    # de pago recorrería la tabla completa.
    op.create_index(op.f("ix_pagos_token"), "pagos", ["token"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_pagos_token"), table_name="pagos")
    op.drop_index(op.f("ix_pagos_orden"), table_name="pagos")
    op.drop_index(op.f("ix_pagos_user_id"), table_name="pagos")
    op.drop_table("pagos")
    sa.Enum(name="pagostatus").drop(op.get_bind(), checkfirst=True)
