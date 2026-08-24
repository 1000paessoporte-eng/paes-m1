"""Abre todos los temas del árbol: nadie queda bloqueado

El Árbol de Habilidades dejó de impedir entrar a un tema y pasó a recomendar en
qué orden estudiarlo. Los prerequisitos siguen ahí --dibujan los conectores y
el "se apoya en"-- pero ya no cierran nada.

Esta migración abre las filas que quedaron en LOCKED de antes del cambio. Sin
esto, quien ya tenía cuenta seguiría viendo su árbol a medias, porque su
progreso está guardado por usuario y nodo.

Solo toca `status`: no se pierde ni un intento ni un acierto, y el valor LOCKED
se conserva en el enum por si hay que volver atrás.

Revision ID: f2e94c6b81a7
Revises: d5b83f2c7e91
"""

from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

revision: str = "f2e94c6b81a7"
down_revision: str | None = "d5b83f2c7e91"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # `unlocked_at` se rellena solo si estaba vacío: el que ya tenía fecha la
    # conserva, porque es cuándo lo abrió de verdad.
    op.execute(
        text(
            """
            UPDATE user_skill_progress
               SET status = 'UNLOCKED',
                   unlocked_at = COALESCE(unlocked_at, now())
             WHERE status = 'LOCKED'
            """
        )
    )


def downgrade() -> None:
    # No se puede deshacer con fidelidad: no queda registro de cuáles estaban
    # bloqueados. Volver atrás significa cambiar el default en el modelo y
    # dejar que `_recompute_unlocks` reconstruya los estados con las reglas de
    # prerequisitos, que es exactamente lo que hacía antes.
    pass
