"""workouts table

Revision ID: 8476a6a1c2be
Revises: 58645a2d9c81
Create Date: 2025-01-02 23:17:41.773718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8476a6a1c2be'
down_revision = '58645a2d9c81'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('workout',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('reps', sa.Integer(), nullable=False),
    sa.Column('weight', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('workout', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_workout_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_workout_name'), ['name'], unique=True)
        batch_op.create_index(batch_op.f('ix_workout_user_id'), ['user_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workout', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_workout_user_id'))
        batch_op.drop_index(batch_op.f('ix_workout_name'))
        batch_op.drop_index(batch_op.f('ix_workout_date'))

    op.drop_table('workout')
    # ### end Alembic commands ###
