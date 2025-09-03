"""no-op: keep quantity as INTEGER; align history"""

from alembic import op
import sqlalchemy as sa

# Alembic identifiers
revision = "c1c8bd37f497"
down_revision = "123b807d6d8c"
branch_labels = None
depends_on = None

def upgrade():
    # Intentionally do nothing. We are keeping quantity as INTEGER.
    pass

def downgrade():
    # Intentionally do nothing.
    pass
