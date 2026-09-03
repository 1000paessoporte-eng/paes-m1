"""Carreras: región y comuna para filtrar el catálogo por ubicación

Dos columnas nullable en `carreras`:

- `region` y `comuna`: dónde se dicta la carrera. No se derivan de `sede`, que
  es texto libre del PDF del DEMRE; salen de la base oficial de matrícula del
  SIES (Mineduc), cruzada por universidad+sede+carrera en
  `scripts/asignar_geo_carreras.py`.

Van nullable a propósito: el cruce con el SIES no encuentra el 100% de las
1.855 carreras (typos de sede, campus sin ciudad), y una carrera sin geo tiene
que poder existir igual. El filtro por región/comuna simplemente no la incluye.

Migración puramente aditiva: la API vieja sigue funcionando sin enterarse, así
que es segura de aplicar antes del merge.

Revision ID: b7d4e9f21a08
Revises: 3112bafe869c
Create Date: 2026-09-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b7d4e9f21a08"
down_revision: str | Sequence[str] | None = "3112bafe869c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("carreras", sa.Column("region", sa.String(length=80), nullable=True))
    op.add_column("carreras", sa.Column("comuna", sa.String(length=80), nullable=True))
    op.create_index("ix_carreras_region", "carreras", ["region"])
    op.create_index("ix_carreras_comuna", "carreras", ["comuna"])


def downgrade() -> None:
    op.drop_index("ix_carreras_comuna", table_name="carreras")
    op.drop_index("ix_carreras_region", table_name="carreras")
    op.drop_column("carreras", "comuna")
    op.drop_column("carreras", "region")
