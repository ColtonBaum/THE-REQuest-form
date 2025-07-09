"""Add parent_id to asset for trailer linkage

Revision ID: aabcbb8a8e82
Revises: 958024863fb0
Create Date: 2025-07-09 10:39:23.845109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aabcbb8a8e82'
down_revision: Union[str, Sequence[str], None] = '958024863fb0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
