"""merge heads: baseline + quantity change"""

from alembic import op
import sqlalchemy as sa

# MERGE migration: unify two heads into one
revision = "572d3b429194"                      # must match filename prefix
down_revision = ("123b807d6d8c", "c1c8bd37f497")  # BOTH current heads
branch_labels = None
depends_on = None

def upgrade():
    # No schema ops; this just merges lineages.
    pass

def downgrade():
    # No schema ops; this would split lineages again.
    pass
