"""Las lecciones pueden traer más de un ejemplo resuelto

Un solo ejercicio resuelto alcanza para ver el procedimiento una vez, pero no
para reconocerlo cuando viene en otra forma --y es en la segunda forma donde el
alumno se cae.

Una columna JSON y no columnas numeradas: agregar un tercer ejemplo tiene que
ser escribirlo, no migrar la tabla otra vez. Nace con `server_default '[]'`, de
modo que las 95 lecciones que ya existen quedan con la lista vacía sin un UPDATE
aparte y la columna puede ser NOT NULL desde el principio.

Revision ID: c3a8b5d21e47
Revises: b7d4e9f1a2c3
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c3a8b5d21e47"
down_revision: str | None = "b7d4e9f1a2c3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "lessons",
        sa.Column(
            "extra_examples",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("lessons", "extra_examples")
