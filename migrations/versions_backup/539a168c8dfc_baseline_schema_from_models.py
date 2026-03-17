"""baseline schema from models

Revision ID: 539a168c8dfc
Revises: 8ca45fde8841
Create Date: 2025-09-03 15:11:34.821232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '539a168c8dfc'
down_revision: Union[str, Sequence[str], None] = '8ca45fde8841'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
