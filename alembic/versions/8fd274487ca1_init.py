"""Init

Revision ID: 8fd274487ca1
Revises: 
Create Date: 2022-09-07 06:55:19.608768

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '8fd274487ca1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('user_name', sa.String(length=32), nullable=True),
    sa.Column('pub_key', sa.String(length=250), nullable=False, default = "0"),
    sa.Column('ip', sa.String(length=20), nullable=False, default = "0"),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False, default = datetime.now()),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, default = datetime.now()),
    sa.Column('is_baned', sa.Boolean(), nullable=True, default = False),
    sa.Column('is_pay', sa.Boolean(), nullable=True, default = True),
    sa.PrimaryKeyConstraint('user_id')
    )


def downgrade() -> None:
    op.drop_table('users')