"""prod: quantity -> VARCHAR(64); relax NOT NULL (Postgres-only)"""

from alembic import op
import sqlalchemy as sa

# Set this to the *generated* revision ID for this file.
revision = "<REV_ID>"
down_revision = "c1c8bd37f497"
branch_labels = None
depends_on = None


def upgrade():
    # Only run the raw SQL on Postgres; no-op on SQLite (already correct locally).
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE request_item "
            "ALTER COLUMN quantity TYPE VARCHAR(64) USING quantity::text"
        )
        op.execute(
            "ALTER TABLE request_item "
            "ALTER COLUMN quantity DROP NOT NULL"
        )
        op.execute(
            "ALTER TABLE request_item "
            "ALTER COLUMN item_name DROP NOT NULL"
        )
    else:
        # SQLite/local is already on VARCHAR + nullable from your models baseline
        pass


def downgrade():
    # Reverse for Postgres; no-op elsewhere.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # Cast text back to integer (empty -> NULL), then re-apply NOT NULLs
        op.execute(
            "ALTER TABLE request_item "
            "ALTER COLUMN quantity TYPE INTEGER USING NULLIF(quantity,'')::integer"
        )
        op.execute(
            "ALTER TABLE request_item "
            "ALTER COLUMN quantity SET NOT NULL"
        )
        op.execute(
            "ALTER TABLE request_item "
            "ALTER COLUMN item_name SET NOT NULL"
        )
    else:
        pass
