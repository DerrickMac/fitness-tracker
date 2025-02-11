"""add muscle_group to Workout model

Revision ID: 26edf191d8ff
Revises: 4c93e765f522
Create Date: 2025-02-08 17:22:33.987463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26edf191d8ff'
down_revision = '4c93e765f522'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workout', schema=None) as batch_op:
        batch_op.add_column(sa.Column('muscle_group', sa.String(length=64), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workout', schema=None) as batch_op:
        batch_op.drop_column('muscle_group')

    # ### end Alembic commands ###
