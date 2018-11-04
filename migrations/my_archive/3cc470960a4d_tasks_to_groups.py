"""tasks to groups

Revision ID: 3cc470960a4d
Revises: 0848b3220278
Create Date: 2018-11-03 11:19:49.923147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3cc470960a4d'
down_revision = '0848b3220278'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tasks_to_groups',
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['task.id'], )
    )
    op.create_foreign_key(None, 'user', 'role', ['role_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_table('tasks_to_groups')
    # ### end Alembic commands ###