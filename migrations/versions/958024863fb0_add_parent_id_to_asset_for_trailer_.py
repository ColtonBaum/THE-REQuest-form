"""Add parent_id to asset for trailer linkage

Revision ID: 958024863fb0
Revises: 2a146b0f97db
Create Date: 2025-07-09 10:35:55.539221

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '958024863fb0'
down_revision: Union[str, Sequence[str], None] = '2a146b0f97db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
