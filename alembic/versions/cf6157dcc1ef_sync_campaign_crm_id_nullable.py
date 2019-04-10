"""sync_campaign crm_id nullable

Revision ID: cf6157dcc1ef
Revises: 65a4fe44fea4
Create Date: 2019-03-29 13:38:12.171684

"""

# revision identifiers, used by Alembic.
revision = 'cf6157dcc1ef'
down_revision = '65a4fe44fea4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('sync_campaign', schema=None) as batch_op:
        batch_op.alter_column('crm_id',
               existing_type=sa.VARCHAR(length=40),
               nullable=True)


def downgrade():
    with op.batch_alter_table('sync_campaign', schema=None) as batch_op:
        batch_op.alter_column('crm_id',
               existing_type=sa.VARCHAR(length=40),
               nullable=False)
