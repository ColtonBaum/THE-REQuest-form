from alembic import op
import sqlalchemy as sa

revision = "8ca45fde8841"
down_revision = "aabcbb8a8e82"
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("request_item", schema=None) as batch_op:
        batch_op.alter_column(
            "quantity",
            existing_type=sa.Integer(),
            type_=sa.String(length=64),
            existing_nullable=False,
            nullable=True,
        )
        batch_op.alter_column(
            "item_name",
            existing_type=sa.String(length=200),
            existing_nullable=False,
            nullable=True,
        )

def downgrade():
    with op.batch_alter_table("request_item", schema=None) as batch_op:
        batch_op.alter_column(
            "item_name",
            existing_type=sa.String(length=200),
            existing_nullable=True,
            nullable=False,
        )
        batch_op.alter_column(
            "quantity",
            existing_type=sa.String(length=64),
            type_=sa.Integer(),
            existing_nullable=True,
            nullable=False,
        )
