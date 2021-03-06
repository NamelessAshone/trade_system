"""create migration scripts

Revision ID: cdca8d8433d0
Revises: 198b0eebcf9
Create Date: 2018-05-09 20:11:42.049439

"""

# revision identifiers, used by Alembic.
revision = 'cdca8d8433d0'
down_revision = '198b0eebcf9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_id')
    op.drop_table('putaway_logs')
    op.drop_table('putaway_log')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('putaway_log',
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('good_id', sa.INTEGER(), nullable=False),
    sa.Column('date', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['good_id'], ['goods.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'good_id')
    )
    op.create_table('putaway_logs',
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('good_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['good_id'], ['goods.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table('user_id',
    sa.Column('good_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['good_id'], ['goods.id'], )
    )
    # ### end Alembic commands ###
