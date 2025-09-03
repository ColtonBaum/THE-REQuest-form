"""prod: quantity -> VARCHAR(64); relax NOT NULL (Postgres-only)"""

from alembic import op
import sqlalchemy as sa

revision = "<PUT_THE_GENERATED_ID_HERE>"
down_revision = "c1c8bd37f497"
branch_labels = None
depends_on = None

def upgrade():
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

def downgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE request_item "
            "ALTER COLUMN quantity TYPE INTEGER USING NULLIF(quantity,'')::integer"
        )
        op.execute("ALTER TABLE request_item ALTER COLUMN quantity SET NOT NULL")
        op.execute("ALTER TABLE request_item ALTER COLUMN item_name SET NOT NULL")
