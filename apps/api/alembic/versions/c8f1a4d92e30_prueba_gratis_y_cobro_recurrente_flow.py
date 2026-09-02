"""prueba gratis de 3 dias y cobro recurrente con Flow

Revision ID: c8f1a4d92e30
Revises: b7d4e9f21a08
Create Date: 2026-09-02

Tres cosas, en el orden en que hay que aplicarlas:

1. `flow_customers`: donde vive la relacion entre un usuario y el cliente de
   Flow que guarda su tarjeta. Acá no hay ni puede haber datos de tarjeta.
2. Tres columnas nuevas en `subscriptions` para el cobro recurrente.
3. El valor TRIAL en el enum `origen`.

Las columnas booleanas entran en tres pasos --nullable, UPDATE, NOT NULL--
porque `subscriptions` ya tiene filas en produccion y una columna NOT NULL sin
valor por defecto sobre una tabla poblada falla al aplicarse. Es exactamente la
trampa que ya rompio produccion el 2026-08-14 y que esta anotada en CLAUDE.md.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'c8f1a4d92e30'
down_revision: str | Sequence[str] | None = 'b7d4e9f21a08'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'flow_customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.String(length=60), nullable=False),
        sa.Column('registrado', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('marca', sa.String(length=40), nullable=True),
        sa.Column('ultimos4', sa.String(length=4), nullable=True),
        sa.Column('token_registro', sa.String(length=120), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_flow_customers_user_id'), 'flow_customers', ['user_id'], unique=True
    )
    op.create_index(
        op.f('ix_flow_customers_customer_id'),
        'flow_customers',
        ['customer_id'],
        unique=True,
    )
    op.create_index(
        op.f('ix_flow_customers_token_registro'),
        'flow_customers',
        ['token_registro'],
        unique=False,
    )

    # `flow_subscription_id` nace nullable y asi se queda: las suscripciones
    # que vienen de un codigo promocional o de un otorgamiento manual no tienen
    # contraparte en la pasarela, y nunca la van a tener.
    op.add_column(
        'subscriptions',
        sa.Column('flow_subscription_id', sa.String(length=60), nullable=True),
    )
    op.create_index(
        op.f('ix_subscriptions_flow_subscription_id'),
        'subscriptions',
        ['flow_subscription_id'],
        unique=False,
    )

    # Los dos booleanos, en tres pasos cada uno.
    for columna in ('cancelada_al_terminar', 'en_trial'):
        op.add_column(
            'subscriptions', sa.Column(columna, sa.Boolean(), nullable=True)
        )
        op.execute(
            f'UPDATE subscriptions SET {columna} = false WHERE {columna} IS NULL'
        )
        op.alter_column(
            'subscriptions',
            columna,
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        )

    # El enum `origen` es un tipo nativo de PostgreSQL: agregarle un valor es
    # ALTER TYPE, no una migracion de columna. `IF NOT EXISTS` lo hace
    # reaplicable, y el valor no se USA en esta misma transaccion --solo se
    # agrega--, que es la unica restriccion que impone PostgreSQL.
    #
    # Va dentro de un guardia por dialecto porque SQLite no tiene tipos enum:
    # ahi las columnas Enum son VARCHAR con un CHECK y no hay nada que alterar.
    if op.get_bind().dialect.name == 'postgresql':
        op.execute("ALTER TYPE origen ADD VALUE IF NOT EXISTS 'TRIAL'")


def downgrade() -> None:
    """Downgrade schema.

    El valor TRIAL del enum NO se quita: PostgreSQL no sabe eliminar un valor
    de un enum sin recrear el tipo y reescribir cada columna que lo use, y
    dejar el valor de mas es inofensivo. Bajar de version tampoco deberia
    borrar el rastro de quien tuvo una prueba.
    """
    op.drop_index(op.f('ix_subscriptions_flow_subscription_id'), table_name='subscriptions')
    op.drop_column('subscriptions', 'en_trial')
    op.drop_column('subscriptions', 'cancelada_al_terminar')
    op.drop_column('subscriptions', 'flow_subscription_id')

    op.drop_index(op.f('ix_flow_customers_token_registro'), table_name='flow_customers')
    op.drop_index(op.f('ix_flow_customers_customer_id'), table_name='flow_customers')
    op.drop_index(op.f('ix_flow_customers_user_id'), table_name='flow_customers')
    op.drop_table('flow_customers')
