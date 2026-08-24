"""Marca los ensayos rendidos demasiado rápido para no leerlos

Un ensayo de veinte preguntas contestado en veintiún segundos entraba al
historial, al mejor puntaje, a los promedios del panel y --desde el plan
Colegios-- a la tabla que el profesor mira para saber cómo va su curso. No es
trampa: es alguien haciendo clic sin leer, que es un comportamiento normal.
Pero sus 260 puntos no dicen nada de lo que esa persona sabe.

La columna es aditiva y con default `true`: los ensayos que ya existen quedan
como representativos, que es lo correcto --nadie puede saber hoy cuáles se
rindieron en serio, y marcarlos a todos de golpe borraría historial real.

Revision ID: d5b83f2c7e91
Revises: a3c7e1d20f45
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d5b83f2c7e91"
down_revision: str | None = "a3c7e1d20f45"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "exam_attempts",
        sa.Column(
            "representativo",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )


def downgrade() -> None:
    op.drop_column("exam_attempts", "representativo")
