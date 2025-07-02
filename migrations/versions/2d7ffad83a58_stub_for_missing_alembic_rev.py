"""stub for missing Alembic rev

Revision ID: 2d7ffad83a58
Revises: 8bac7ba2c203
Create Date: 2025-07-01 17:55:46.256348

"""
from alembic import op
import sqlalchemy as sa


# … in 2d7ffad83a58_stub_for_missing_alembic_rev.py …

# revision identifiers, used by Alembic.
revision = '2d7ffad83a58'
# chain *after* the add_notes migration
down_revision = '8bac7ba2c203'
branch_labels = None
depends_on = None

def upgrade():
    # stub: nothing to do
    pass

def downgrade():
    pass
