"""describe change

Revision ID: 2a146b0f97db
Revises: ffab0786d5b1
Create Date: 2025-07-02 10:25:39.580919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a146b0f97db'
down_revision: Union[str, Sequence[str], None] = 'ffab0786d5b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
