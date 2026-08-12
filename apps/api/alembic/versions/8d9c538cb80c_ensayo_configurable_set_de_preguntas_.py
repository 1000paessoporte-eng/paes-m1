"""ensayo configurable: set de preguntas, ritmo, ejes y puntaje

Revision ID: 8d9c538cb80c
Revises: 6edb328c5595
Create Date: 2026-08-12 15:35:15.109732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8d9c538cb80c'
down_revision: Union[str, Sequence[str], None] = '6edb328c5595'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# En PostgreSQL, add_column con un Enum NO crea el tipo por sí solo: hay que
# crearlo antes y referenciarlo con create_type=False.
pace_enum = sa.Enum('OFICIAL', 'EXIGENTE', 'RELAJADO', name='pace')


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('exam_attempt_questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('attempt_id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['attempt_id'], ['exam_attempts.id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exam_attempt_questions_attempt_id'), 'exam_attempt_questions', ['attempt_id'], unique=False)
    op.create_index(op.f('ix_exam_attempt_questions_question_id'), 'exam_attempt_questions', ['question_id'], unique=False)
    op.add_column('exam_answers', sa.Column('flagged', sa.Boolean(), server_default='false', nullable=False))

    pace_enum.create(op.get_bind(), checkfirst=True)
    # server_default: los intentos ya rendidos fueron a ritmo oficial (era el
    # único que existía), así que ese es el valor correcto para las filas viejas.
    op.add_column(
        'exam_attempts',
        sa.Column(
            'pace',
            postgresql.ENUM('OFICIAL', 'EXIGENTE', 'RELAJADO', name='pace', create_type=False),
            nullable=False,
            server_default='OFICIAL',
        ),
    )
    op.add_column('exam_attempts', sa.Column('axes', sa.String(length=200), nullable=True))
    op.add_column('exam_attempts', sa.Column('estimated_score', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('exam_attempts', 'estimated_score')
    op.drop_column('exam_attempts', 'axes')
    op.drop_column('exam_attempts', 'pace')
    pace_enum.drop(op.get_bind(), checkfirst=True)
    op.drop_column('exam_answers', 'flagged')
    op.drop_index(op.f('ix_exam_attempt_questions_question_id'), table_name='exam_attempt_questions')
    op.drop_index(op.f('ix_exam_attempt_questions_attempt_id'), table_name='exam_attempt_questions')
    op.drop_table('exam_attempt_questions')
