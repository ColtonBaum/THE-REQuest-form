"""Phase 3a: Add file upload support for requests

Revision ID: phase3a_file_uploads
Revises: phase2b_fix_orphans
Create Date: 2026-03-17

"""
from alembic import op
import sqlalchemy as sa

revision = 'phase3a_file_uploads'
down_revision = 'phase2b_fix_orphans'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'request_file',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('request_id', sa.Integer, sa.ForeignKey('request.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=True),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('uploaded_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_request_file_request_id', 'request_file', ['request_id'])


def downgrade():
    op.drop_index('ix_request_file_request_id', table_name='request_file')
    op.drop_table('request_file')
