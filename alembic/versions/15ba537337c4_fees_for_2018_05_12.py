"""fees for 2018-05..12

Revision ID: 15ba537337c4
Revises: d4070befe087
Create Date: 2018-04-23 20:17:04.038659

"""

# revision identifiers, used by Alembic.
revision = '15ba537337c4'
down_revision = 'd4070befe087'

from alembic import op
import sqlalchemy as sa
from SqliteDecimal import SqliteDecimal


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dues18_05invoices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invoice_no', sa.Integer(), nullable=True),
    sa.Column('invoice_no_string', sa.Unicode(length=255), nullable=True),
    sa.Column('invoice_date', sa.DateTime(), nullable=True),
    sa.Column('invoice_amount', SqliteDecimal(length=12, collation=2), nullable=True),
    sa.Column('is_cancelled', sa.Boolean(), nullable=True),
    sa.Column('cancelled_date', sa.DateTime(), nullable=True),
    sa.Column('is_reversal', sa.Boolean(), nullable=True),
    sa.Column('is_altered', sa.Boolean(), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('membership_no', sa.Integer(), nullable=True),
    sa.Column('email', sa.Unicode(length=255), nullable=True),
    sa.Column('token', sa.Unicode(length=255), nullable=True),
    sa.Column('preceding_invoice_no', sa.Integer(), nullable=True),
    sa.Column('succeeding_invoice_no', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('invoice_no_string')
    )
    op.create_table('dues18_06invoices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invoice_no', sa.Integer(), nullable=True),
    sa.Column('invoice_no_string', sa.Unicode(length=255), nullable=True),
    sa.Column('invoice_date', sa.DateTime(), nullable=True),
    sa.Column('invoice_amount', SqliteDecimal(length=12, collation=2), nullable=True),
    sa.Column('is_cancelled', sa.Boolean(), nullable=True),
    sa.Column('cancelled_date', sa.DateTime(), nullable=True),
    sa.Column('is_reversal', sa.Boolean(), nullable=True),
    sa.Column('is_altered', sa.Boolean(), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('membership_no', sa.Integer(), nullable=True),
    sa.Column('email', sa.Unicode(length=255), nullable=True),
    sa.Column('token', sa.Unicode(length=255), nullable=True),
    sa.Column('preceding_invoice_no', sa.Integer(), nullable=True),
    sa.Column('succeeding_invoice_no', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('invoice_no_string')
    )
    op.create_table('dues18_07invoices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invoice_no', sa.Integer(), nullable=True),
    sa.Column('invoice_no_string', sa.Unicode(length=255), nullable=True),
    sa.Column('invoice_date', sa.DateTime(), nullable=True),
    sa.Column('invoice_amount', SqliteDecimal(length=12, collation=2), nullable=True),
    sa.Column('is_cancelled', sa.Boolean(), nullable=True),
    sa.Column('cancelled_date', sa.DateTime(), nullable=True),
    sa.Column('is_reversal', sa.Boolean(), nullable=True),
    sa.Column('is_altered', sa.Boolean(), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('membership_no', sa.Integer(), nullable=True),
    sa.Column('email', sa.Unicode(length=255), nullable=True),
    sa.Column('token', sa.Unicode(length=255), nullable=True),
    sa.Column('preceding_invoice_no', sa.Integer(), nullable=True),
    sa.Column('succeeding_invoice_no', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('invoice_no_string')
    )
    op.create_table('dues18_08invoices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invoice_no', sa.Integer(), nullable=True),
    sa.Column('invoice_no_string', sa.Unicode(length=255), nullable=True),
    sa.Column('invoice_date', sa.DateTime(), nullable=True),
    sa.Column('invoice_amount', SqliteDecimal(length=12, collation=2), nullable=True),
    sa.Column('is_cancelled', sa.Boolean(), nullable=True),
    sa.Column('cancelled_date', sa.DateTime(), nullable=True),
    sa.Column('is_reversal', sa.Boolean(), nullable=True),
    sa.Column('is_altered', sa.Boolean(), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('membership_no', sa.Integer(), nullable=True),
    sa.Column('email', sa.Unicode(length=255), nullable=True),
    sa.Column('token', sa.Unicode(length=255), nullable=True),
    sa.Column('preceding_invoice_no', sa.Integer(), nullable=True),
    sa.Column('succeeding_invoice_no', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('invoice_no_string')
    )
    op.create_table('dues18_09invoices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invoice_no', sa.Integer(), nullable=True),
    sa.Column('invoice_no_string', sa.Unicode(length=255), nullable=True),
    sa.Column('invoice_date', sa.DateTime(), nullable=True),
    sa.Column('invoice_amount', SqliteDecimal(length=12, collation=2), nullable=True),
    sa.Column('is_cancelled', sa.Boolean(), nullable=True),
    sa.Column('cancelled_date', sa.DateTime(), nullable=True),
    sa.Column('is_reversal', sa.Boolean(), nullable=True),
    sa.Column('is_altered', sa.Boolean(), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('membership_no', sa.Integer(), nullable=True),
    sa.Column('email', sa.Unicode(length=255), nullable=True),
    sa.Column('token', sa.Unicode(length=255), nullable=True),
    sa.Column('preceding_invoice_no', sa.Integer(), nullable=True),
    sa.Column('succeeding_invoice_no', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('invoice_no_string')
    )
    op.create_table('dues18_10invoices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invoice_no', sa.Integer(), nullable=True),
    sa.Column('invoice_no_string', sa.Unicode(length=255), nullable=True),
    sa.Column('invoice_date', sa.DateTime(), nullable=True),
    sa.Column('invoice_amount', SqliteDecimal(length=12, collation=2), nullable=True),
    sa.Column('is_cancelled', sa.Boolean(), nullable=True),
    sa.Column('cancelled_date', sa.DateTime(), nullable=True),
    sa.Column('is_reversal', sa.Boolean(), nullable=True),
    sa.Column('is_altered', sa.Boolean(), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('membership_no', sa.Integer(), nullable=True),
    sa.Column('email', sa.Unicode(length=255), nullable=True),
    sa.Column('token', sa.Unicode(length=255), nullable=True),
    sa.Column('preceding_invoice_no', sa.Integer(), nullable=True),
    sa.Column('succeeding_invoice_no', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('invoice_no_string')
    )
    op.create_table('dues18_11invoices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invoice_no', sa.Integer(), nullable=True),
    sa.Column('invoice_no_string', sa.Unicode(length=255), nullable=True),
    sa.Column('invoice_date', sa.DateTime(), nullable=True),
    sa.Column('invoice_amount', SqliteDecimal(length=12, collation=2), nullable=True),
    sa.Column('is_cancelled', sa.Boolean(), nullable=True),
    sa.Column('cancelled_date', sa.DateTime(), nullable=True),
    sa.Column('is_reversal', sa.Boolean(), nullable=True),
    sa.Column('is_altered', sa.Boolean(), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('membership_no', sa.Integer(), nullable=True),
    sa.Column('email', sa.Unicode(length=255), nullable=True),
    sa.Column('token', sa.Unicode(length=255), nullable=True),
    sa.Column('preceding_invoice_no', sa.Integer(), nullable=True),
    sa.Column('succeeding_invoice_no', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('invoice_no_string')
    )
    op.create_table('dues18_12invoices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('invoice_no', sa.Integer(), nullable=True),
    sa.Column('invoice_no_string', sa.Unicode(length=255), nullable=True),
    sa.Column('invoice_date', sa.DateTime(), nullable=True),
    sa.Column('invoice_amount', SqliteDecimal(length=12, collation=2), nullable=True),
    sa.Column('is_cancelled', sa.Boolean(), nullable=True),
    sa.Column('cancelled_date', sa.DateTime(), nullable=True),
    sa.Column('is_reversal', sa.Boolean(), nullable=True),
    sa.Column('is_altered', sa.Boolean(), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('membership_no', sa.Integer(), nullable=True),
    sa.Column('email', sa.Unicode(length=255), nullable=True),
    sa.Column('token', sa.Unicode(length=255), nullable=True),
    sa.Column('preceding_invoice_no', sa.Integer(), nullable=True),
    sa.Column('succeeding_invoice_no', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('invoice_no_string')
    )
    op.drop_table('dues15invoices')
    op.drop_table('dues17invoices')
    op.drop_table('dues16invoices')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dues16invoices',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('invoice_no', sa.INTEGER(), nullable=True),
    sa.Column('invoice_no_string', sa.VARCHAR(length=255), nullable=True),
    sa.Column('invoice_date', sa.DATETIME(), nullable=True),
    sa.Column('invoice_amount', sa.VARCHAR(length=100), nullable=True),
    sa.Column('is_cancelled', sa.BOOLEAN(), nullable=True),
    sa.Column('cancelled_date', sa.DATETIME(), nullable=True),
    sa.Column('is_reversal', sa.BOOLEAN(), nullable=True),
    sa.Column('is_altered', sa.BOOLEAN(), nullable=True),
    sa.Column('member_id', sa.INTEGER(), nullable=True),
    sa.Column('membership_no', sa.INTEGER(), nullable=True),
    sa.Column('email', sa.VARCHAR(length=255), nullable=True),
    sa.Column('token', sa.VARCHAR(length=255), nullable=True),
    sa.Column('preceding_invoice_no', sa.INTEGER(), nullable=True),
    sa.Column('succeeding_invoice_no', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('invoice_no_string')
    )
    op.create_table('dues17invoices',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('invoice_no', sa.INTEGER(), nullable=True),
    sa.Column('invoice_no_string', sa.VARCHAR(length=255), nullable=True),
    sa.Column('invoice_date', sa.DATETIME(), nullable=True),
    sa.Column('invoice_amount', sa.VARCHAR(length=100), nullable=True),
    sa.Column('is_cancelled', sa.BOOLEAN(), nullable=True),
    sa.Column('cancelled_date', sa.DATETIME(), nullable=True),
    sa.Column('is_reversal', sa.BOOLEAN(), nullable=True),
    sa.Column('is_altered', sa.BOOLEAN(), nullable=True),
    sa.Column('member_id', sa.INTEGER(), nullable=True),
    sa.Column('membership_no', sa.INTEGER(), nullable=True),
    sa.Column('email', sa.VARCHAR(length=255), nullable=True),
    sa.Column('token', sa.VARCHAR(length=255), nullable=True),
    sa.Column('preceding_invoice_no', sa.INTEGER(), nullable=True),
    sa.Column('succeeding_invoice_no', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('invoice_no_string')
    )
    op.create_table('dues15invoices',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('invoice_no', sa.INTEGER(), nullable=True),
    sa.Column('invoice_no_string', sa.VARCHAR(length=255), nullable=True),
    sa.Column('invoice_date', sa.DATETIME(), nullable=True),
    sa.Column('invoice_amount', sa.VARCHAR(length=100), nullable=True),
    sa.Column('is_cancelled', sa.BOOLEAN(), nullable=True),
    sa.Column('cancelled_date', sa.DATETIME(), nullable=True),
    sa.Column('is_reversal', sa.BOOLEAN(), nullable=True),
    sa.Column('is_altered', sa.BOOLEAN(), nullable=True),
    sa.Column('member_id', sa.INTEGER(), nullable=True),
    sa.Column('membership_no', sa.INTEGER(), nullable=True),
    sa.Column('email', sa.VARCHAR(length=255), nullable=True),
    sa.Column('token', sa.VARCHAR(length=255), nullable=True),
    sa.Column('preceding_invoice_no', sa.INTEGER(), nullable=True),
    sa.Column('succeeding_invoice_no', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invoice_no'),
    sa.UniqueConstraint('invoice_no_string')
    )
    op.drop_table('dues18_12invoices')
    op.drop_table('dues18_11invoices')
    op.drop_table('dues18_10invoices')
    op.drop_table('dues18_09invoices')
    op.drop_table('dues18_08invoices')
    op.drop_table('dues18_07invoices')
    op.drop_table('dues18_06invoices')
    op.drop_table('dues18_05invoices')
    # ### end Alembic commands ###
