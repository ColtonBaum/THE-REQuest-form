"""Add notes column to Request

Revision ID: 8bac7ba2c203
Revises: 7d6db8d6c66f
Create Date: 2025-07-01 16:29:23.781521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bac7ba2c203'
down_revision = '7d6db8d6c66f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'request',
        sa.Column('notes', sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_column('request', 'notes')