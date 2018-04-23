"""Invitations for general assembly and bar camp 2018

Revision ID: 34c421bb0d0c
Revises: 2fbe1bde5df8
Create Date: 2018-04-23 20:03:17.014936

"""

# revision identifiers, used by Alembic.
revision = '34c421bb0d0c'
down_revision = '2fbe1bde5df8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('members', sa.Column('email_invite_date_bcgv18', sa.DateTime(), nullable=True))
    op.add_column('members', sa.Column('email_invite_flag_bcgv18', sa.Boolean(), nullable=True))
    op.add_column('members', sa.Column('email_invite_token_bcgv18', sa.Unicode(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('members') as batch_op:
        batch_op.drop_column('email_invite_token_bcgv18')
        batch_op.drop_column('email_invite_flag_bcgv18')
        batch_op.drop_column('email_invite_date_bcgv18')
