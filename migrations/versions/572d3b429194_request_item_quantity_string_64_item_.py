from alembic import op
import sqlalchemy as sa

# Replace with your current head
revision = "CHANGE_ME"
down_revision = "123b807d6d8c"  # your baseline id
branch_labels = None
depends_on = None

def upgrade():
    # change INT -> VARCHAR(64) and allow NULLs (Postgres needs USING)
    with op.batch_alter_table("request_item") as b:
        b.alter_column(
            "quantity",
            existing_type=sa.Integer(),
            type_=sa.String(64),
            existing_nullable=False,   # if it was NOT NULL before
            nullable=True,
            postgresql_using="quantity::text",
        )
        # make item_name nullable (if it isn’t already)
        b.alter_column(
            "item_name",
            existing_type=sa.String(length=200),
            nullable=True,
        )

def downgrade():
    with op.batch_alter_table("request_item") as b:
        # revert item_name to NOT NULL (if desired)
        b.alter_column(
            "item_name",
            existing_type=sa.String(length=200),
            nullable=False,
        )
        # change VARCHAR -> INT and NOT NULL; cast text to int
        b.alter_column(
            "quantity",
            existing_type=sa.String(length=64),
            type_=sa.Integer(),
            existing_nullable=True,
            nullable=False,
            postgresql_using="NULLIF(regexp_replace(quantity, '[^0-9-]', '', 'g'),'')::integer",
        )
