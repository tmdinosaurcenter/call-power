"""sync_campaign_schedule_options

Revision ID: 3b2f5b729b7a
Revises: cf6157dcc1ef
Create Date: 2019-05-07 13:42:16.785960

"""

# revision identifiers, used by Alembic.
revision = '3b2f5b729b7a'
down_revision = 'cf6157dcc1ef'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('sync_campaign', schema=None) as batch_op:
        batch_op.add_column(sa.Column('schedule', sa.String(length=25), nullable=True, server_default='hourly'))
        batch_op.alter_column('job_id', existing_type=sa.String(length=36), nullable=True)

def downgrade():
    with op.batch_alter_table('sync_campaign', schema=None) as batch_op:
        batch_op.drop_column('schedule')
        batch_op.alter_column('job_id', existing_type=sa.String(length=36), nullable=False)
