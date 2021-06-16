"""increase target phonenumber length to allow long extensions

Revision ID: 0dde2debce11
Revises: 31535a02650a
Create Date: 2021-06-16 13:51:15.304456

"""

# revision identifiers, used by Alembic.
revision = '0dde2debce11'
down_revision = '31535a02650a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy_utils.types

def upgrade():
    with op.batch_alter_table('campaign_target', schema=None) as batch_op:
        batch_op.alter_column('number',
               existing_type=sa.VARCHAR(length=20),
               type_=sqlalchemy_utils.types.phone_number.PhoneNumberType(max_length=23),
               existing_nullable=True)

    with op.batch_alter_table('campaign_target_office', schema=None) as batch_op:
        batch_op.alter_column('number',
               existing_type=sa.VARCHAR(length=20),
               type_=sqlalchemy_utils.types.phone_number.PhoneNumberType(max_length=23),
               existing_nullable=True)

def downgrade():
    with op.batch_alter_table('campaign_target', schema=None) as batch_op:
        batch_op.alter_column('number',
               existing_type=sqlalchemy_utils.types.phone_number.PhoneNumberType(max_length=23),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)

    with op.batch_alter_table('campaign_target_office', schema=None) as batch_op:
        batch_op.alter_column('number',
               existing_type=sqlalchemy_utils.types.phone_number.PhoneNumberType(max_length=23),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)
