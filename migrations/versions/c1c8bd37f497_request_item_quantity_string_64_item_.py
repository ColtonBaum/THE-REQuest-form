"""request_item.quantity -> String(64); item_name nullable"""

from alembic import op
import sqlalchemy as sa

# Alembic identifiers
revision = "c1c8bd37f497"         # <- keep this exactly as your filename prefix
down_revision = "123b807d6d8c"    # <- your baseline revision id
branch_labels = None
depends_on = None


def upgrade():
    # Postgres-safe type change: INT -> VARCHAR(64), allow NULLs
    # The USING clause casts existing ints to text so the change succeeds
    with op.batch_alter_table("request_item") as b:
        b.alter_column(
            "quantity",
            existing_type=sa.Integer(),
            type_=sa.String(64),
            existing_nullable=False,   # old column was NOT NULL in your original schema
            nullable=True,
            postgresql_using="quantity::text",
        )
        # Make item_name nullable (fits your new “not every line required” rule)
        b.alter_column(
            "item_name",
            existing_type=sa.String(length=200),
            nullable=True,
        )


def downgrade():
    # Revert item_name to NOT NULL and quantity back to INT NOT NULL
    with op.batch_alter_table("request_item") as b:
        b.alter_column(
            "item_name",
            existing_type=sa.String(length=200),
            nullable=False,
        )
        # Cast text back to integer; strip non-digits and treat empty as NULL, then ::integer
        b.alter_column(
            "quantity",
            existing_type=sa.String(length=64),
            type_=sa.Integer(),
            existing_nullable=True,
            nullable=False,
            postgresql_using="NULLIF(regexp_replace(quantity, '[^0-9-]', '', 'g'),'')::integer",
        )
