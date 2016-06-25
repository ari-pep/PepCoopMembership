"""empty message

Revision ID: 1a6cbb61c557
Revises: 35c80a305f9d
Create Date: 2014-09-04 09:56:15.636243

"""

# revision identifiers, used by Alembic.
revision = '1a6cbb61c557'
down_revision = '35c80a305f9d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('members', sa.Column('certificate_email', sa.Boolean(), nullable=True))
    op.add_column('members', sa.Column('certificate_email_date', sa.DateTime(), nullable=True))
    op.add_column('members', sa.Column('certificate_token', sa.Unicode(length=10), nullable=True))
    ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('members') as batch_op:
        batch_op.drop_column('certificate_token')
        batch_op.drop_column('certificate_email_date')
        batch_op.drop_column('certificate_email')
