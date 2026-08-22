"""Plan Colegios y registro de errores del navegador

Tres cosas que hasta ahora se prometían o se perdían:

- `colegios` y `ensayos_programados`: el plan Colegios existía en la página de
  precios pero no en el producto. Un curso tiene un código corto que el
  profesor reparte; los alumnos se suman con ese código.
- `users.colegio_id` y `users.es_profesor`: a qué curso pertenece cada cuenta y
  quién lo administra. Ambas admiten NULL/false, así que las 7 cuentas que ya
  existen no necesitan relleno.
- `errores_cliente`: hasta ahora un error de JavaScript en el navegador de un
  estudiante no dejaba rastro en ninguna parte. Se agrupa por mensaje y ruta
  con un contador, para que mil veces el mismo error sea una fila y no mil.

Revision ID: a3c7e1d20f45
Revises: f1a7c30b94e6
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a3c7e1d20f45"
down_revision: str | None = "f1a7c30b94e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "colegios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=160), nullable=False),
        sa.Column("codigo", sa.String(length=8), nullable=False),
        sa.Column("creado_por", sa.Integer(), nullable=True),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("plan_hasta", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["creado_por"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    # Único de verdad en la base: el código se genera al azar y se reintenta
    # ante colisión, y esta restricción es la que hace que ese reintento tenga
    # sentido.
    op.create_index("ix_colegios_codigo", "colegios", ["codigo"], unique=True)

    op.create_table(
        "ensayos_programados",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("colegio_id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=160), nullable=False),
        # Los tipos enum `subject` y `pace` ya existen en la base desde las
        # migraciones de ensayos. Sin create_type=False, alembic intenta
        # crearlos otra vez y la migración se cae con "type already exists".
        sa.Column(
            "subject",
            postgresql.ENUM(name="subject", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "pace",
            postgresql.ENUM(name="pace", create_type=False),
            nullable=False,
        ),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["colegio_id"], ["colegios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_ensayos_programados_colegio_id",
        "ensayos_programados",
        ["colegio_id"],
    )
    op.create_index("ix_ensayos_programados_fecha", "ensayos_programados", ["fecha"])
    op.create_index("ix_colegios_creado_por", "colegios", ["creado_por"])

    op.add_column("users", sa.Column("colegio_id", sa.Integer(), nullable=True))
    op.create_index("ix_users_colegio_id", "users", ["colegio_id"])
    op.create_foreign_key(
        "fk_users_colegio_id", "users", "colegios", ["colegio_id"], ["id"]
    )
    op.add_column(
        "users",
        sa.Column(
            "es_profesor",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.create_table(
        "errores_cliente",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("mensaje", sa.String(length=500), nullable=False),
        sa.Column("ruta", sa.String(length=255), nullable=False),
        sa.Column("pila", sa.Text(), nullable=True),
        sa.Column("navegador", sa.String(length=60), nullable=True),
        sa.Column(
            "ocurrido_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("veces", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_errores_cliente_ocurrido_en", "errores_cliente", ["ocurrido_en"])
    op.create_index("ix_errores_cliente_user_id", "errores_cliente", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_errores_cliente_user_id", table_name="errores_cliente")
    op.drop_index("ix_errores_cliente_ocurrido_en", table_name="errores_cliente")
    op.drop_table("errores_cliente")

    op.drop_column("users", "es_profesor")
    op.drop_constraint("fk_users_colegio_id", "users", type_="foreignkey")
    op.drop_index("ix_users_colegio_id", table_name="users")
    op.drop_column("users", "colegio_id")

    op.drop_index("ix_colegios_creado_por", table_name="colegios")
    op.drop_index("ix_ensayos_programados_fecha", table_name="ensayos_programados")
    op.drop_index("ix_ensayos_programados_colegio_id", table_name="ensayos_programados")
    op.drop_table("ensayos_programados")
    op.drop_index("ix_colegios_codigo", table_name="colegios")
    op.drop_table("colegios")
