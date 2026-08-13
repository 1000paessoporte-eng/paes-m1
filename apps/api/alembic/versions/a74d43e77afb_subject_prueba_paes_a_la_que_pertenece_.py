"""subject: prueba PAES a la que pertenece cada nodo e intento

Revision ID: a74d43e77afb
Revises: 4b4def55d69c
Create Date: 2026-08-13 17:49:46.762849

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a74d43e77afb'
down_revision: Union[str, Sequence[str], None] = '4b4def55d69c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# El tipo se usa en dos columnas dentro de esta misma migracion: se crea una
# sola vez explicitamente y se reusa con create_type=False, si no Alembic
# intenta crearlo de nuevo en el segundo add_column y falla.
subject_enum = postgresql.ENUM('M1', 'M2', name='subject')


def upgrade() -> None:
    """Upgrade schema."""
    subject_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'exam_attempts',
        sa.Column('subject', subject_enum, server_default='M1', nullable=False),
    )
    op.add_column(
        'skill_nodes',
        sa.Column(
            'subject',
            postgresql.ENUM('M1', 'M2', name='subject', create_type=False),
            server_default='M1',
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('skill_nodes', 'subject')
    op.drop_column('exam_attempts', 'subject')
    subject_enum.drop(op.get_bind(), checkfirst=True)
