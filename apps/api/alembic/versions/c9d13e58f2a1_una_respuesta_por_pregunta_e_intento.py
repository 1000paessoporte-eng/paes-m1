"""exam_answers: una respuesta por pregunta e intento

Revision ID: c9d13e58f2a1
Revises: b7c2e9f14a30
Create Date: 2026-08-20

Dos guardados simultáneos de la misma pregunta creaban dos filas. A partir de
ahí el propio guardado reventaba al leerlas y esa pregunta quedaba inservible
por el resto del ensayo, contada como omitida aunque el alumno la respondiera.

Los duplicados que ya existan se limpian ANTES de crear la restricción: si no,
la migración falla en cualquier base que tenga uno. Se conserva la fila más
reciente por (intento, pregunta), que es la respuesta que el alumno dejó
última; el resto se borra.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c9d13e58f2a1"
down_revision: str | Sequence[str] | None = "b7c2e9f14a30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Se conserva el id más alto de cada par: es la fila insertada después y,
    # por tanto, la que refleja lo último que hizo el alumno.
    op.execute(
        sa.text(
            """
            DELETE FROM exam_answers
            WHERE id NOT IN (
                SELECT MAX(id) FROM exam_answers GROUP BY attempt_id, question_id
            )
            """
        )
    )
    op.create_unique_constraint(
        "uq_exam_answer_intento_pregunta", "exam_answers", ["attempt_id", "question_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_exam_answer_intento_pregunta", "exam_answers", type_="unique")
