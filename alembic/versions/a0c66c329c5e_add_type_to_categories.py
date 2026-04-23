"""Add type to categories

Revision ID: a0c66c329c5e
Revises: 55a8e88bdf3e
Create Date: 2026-04-23 12:20:57.959783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0c66c329c5e'
down_revision: Union[str, None] = '55a8e88bdf3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('categories', sa.Column('type', sa.String(), nullable=True, server_default='expense'))


def downgrade() -> None:
    op.drop_column('categories', 'type')
