"""merge heads: baseline + quantity change"""

from alembic import op
import sqlalchemy as sa

# This is the MERGE migration.
# Use the filename prefix as revision, and list BOTH heads in down_revisions.
revision = "572d3b429194"
down_revisions = ("123b807d6d8c", "c1c8bd37f497")
branch_labels = None
depends_on = None

def upgrade():
    # No schema changes; this just merges the two heads into one.
    pass

def downgrade():
    # Split the heads again (rarely used). Also no schema ops here.
    pass
