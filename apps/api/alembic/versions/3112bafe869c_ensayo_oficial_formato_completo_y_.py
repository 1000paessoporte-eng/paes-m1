"""Ensayo oficial: formato completo y registro de salidas de la página

Tres columnas en `exam_attempts`:

- `oficial`: el ensayo se rindió con la prueba completa y la duración exacta
  del DEMRE, no con una configuración a medida.
- `salidas` y `segundos_fuera`: cuántas veces el estudiante dejó la página
  durante el ensayo y cuánto tiempo estuvo fuera. No invalidan nada; se
  muestran al terminar, porque rendir la prueba real son dos horas y media
  sin levantarse de la silla.

Las tres llevan server_default, así que los intentos que ya existen quedan
como lo que fueron: no oficiales y sin salidas registradas.

NOTA: el autogenerate propuso además tocar las claves foráneas de
`ensayos_programados` y `errores_cliente` --perdiendo sus ondelete-- y borrar
un índice de `page_views`. Nada de eso pertenece a este cambio y se quitó a
mano.

Revision ID: 3112bafe869c
Revises: f2e94c6b81a7
Create Date: 2026-08-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "3112bafe869c"
down_revision: str | Sequence[str] | None = "f2e94c6b81a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "exam_attempts",
        sa.Column("oficial", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "exam_attempts",
        sa.Column("salidas", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "exam_attempts",
        sa.Column("segundos_fuera", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("exam_attempts", "segundos_fuera")
    op.drop_column("exam_attempts", "salidas")
    op.drop_column("exam_attempts", "oficial")
