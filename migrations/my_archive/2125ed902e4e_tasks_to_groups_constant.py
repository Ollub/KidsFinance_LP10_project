"""tasks to groups constant

Revision ID: 2125ed902e4e
Revises: 0848b3220278
Create Date: 2018-11-03 11:44:50.024948

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2125ed902e4e'
down_revision = '0848b3220278'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'user', 'role', ['role_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    # ### end Alembic commands ###