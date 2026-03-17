"""Phase 2: Add equipment assignment to requests, search indexes

Revision ID: phase2_001
Revises: d1e2f3a4b5c6
Create Date: 2026-03-16

"""
from alembic import op
import sqlalchemy as sa

revision = 'phase2_001'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        return

    # 1. Add equipment_assigned text field to request table
    op.add_column('request', sa.Column('equipment_assigned', sa.Text, nullable=True))

    # 2. Add indexes on asset table for faster searching
    op.create_index('ix_asset_serial_number', 'asset', ['serial_number'])
    op.create_index('ix_asset_identifier', 'asset', ['identifier'])
    op.create_index('ix_asset_group', 'asset', ['group'])


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        return

    op.drop_index('ix_asset_group', table_name='asset')
    op.drop_index('ix_asset_identifier', table_name='asset')
    op.drop_index('ix_asset_serial_number', table_name='asset')
    op.drop_column('request', 'equipment_assigned')
