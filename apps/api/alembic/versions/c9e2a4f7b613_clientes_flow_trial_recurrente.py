"""Clientes de Flow para el trial con tarjeta y cobro recurrente

Una tabla `clientes_flow`: el vínculo de cada usuario con Flow para cobrarle mes
a mes. Guarda el id del cliente y el de la suscripción que Flow devuelve, el
token del registro de tarjeta en curso, y en qué punto del cobro está
(registrando / trial / activa / cancelada / fallida).

Es aditiva y no toca `subscriptions` ni `pagos`: el acceso lo sigue decidiendo
`Subscription`, esto solo registra cómo cobra Flow. Segura de aplicar antes del
merge.

Revision ID: c9e2a4f7b613
Revises: b7d4e9f21a08
Create Date: 2026-09-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c9e2a4f7b613"
down_revision: str | Sequence[str] | None = "b7d4e9f21a08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ESTADO = sa.Enum(
    "REGISTRANDO",
    "TRIAL",
    "ACTIVA",
    "CANCELADA",
    "FALLIDA",
    name="estadoflow",
)


def upgrade() -> None:
    op.create_table(
        "clientes_flow",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("flow_customer_id", sa.String(length=80), nullable=True),
        sa.Column("flow_subscription_id", sa.String(length=80), nullable=True),
        sa.Column("registro_token", sa.String(length=120), nullable=True),
        sa.Column("status", _ESTADO, nullable=False, server_default="REGISTRANDO"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(
        "ix_clientes_flow_user_id", "clientes_flow", ["user_id"], unique=True
    )
    op.create_index(
        "ix_clientes_flow_flow_subscription_id",
        "clientes_flow",
        ["flow_subscription_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_clientes_flow_flow_subscription_id", table_name="clientes_flow")
    op.drop_index("ix_clientes_flow_user_id", table_name="clientes_flow")
    op.drop_table("clientes_flow")
    _ESTADO.drop(op.get_bind(), checkfirst=True)
