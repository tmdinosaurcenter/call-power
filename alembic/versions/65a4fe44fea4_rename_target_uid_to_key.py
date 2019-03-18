"""rename target.uid to key

Revision ID: 65a4fe44fea4
Revises: 4f2d9aae4765
Create Date: 2019-03-18 11:55:45.209729

"""

# revision identifiers, used by Alembic.
revision = '65a4fe44fea4'
down_revision = '4f2d9aae4765'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('campaign_target', schema=None) as batch_op:
        batch_op.alter_column('uid', new_column_name='key')
        batch_op.create_index(batch_op.f('ix_campaign_target_key'), ['key'], unique=False)
        batch_op.drop_index('ix_campaign_target_uid')


def downgrade():
    with op.batch_alter_table('campaign_target', schema=None) as batch_op:
        batch_op.alter_column('key', new_column_name='uid')
        batch_op.create_index('ix_campaign_target_uid', ['uid'], unique=False)
        batch_op.drop_index(batch_op.f('ix_campaign_target_key'))
