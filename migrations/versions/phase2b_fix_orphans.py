"""Phase 2b: Re-link orphaned jobs to project_manager table

Revision ID: phase2b_fix_orphans
Revises: phase2_001
Create Date: 2026-03-17

"""
from alembic import op
import sqlalchemy as sa

revision = 'phase2b_fix_orphans'
down_revision = 'phase2_001'
branch_labels = None
depends_on = None


def upgrade():
    # Re-run the backfill for any jobs where manager_id is still NULL
    # but the manager string column has a value.
    # Use TRIM and LOWER for fuzzy matching in case of trailing spaces or case diffs.
    op.execute("""
        UPDATE job
        SET manager_id = pm.id
        FROM project_manager pm
        WHERE job.manager_id IS NULL
          AND job.manager IS NOT NULL
          AND LOWER(TRIM(job.manager)) = LOWER(TRIM(pm.name))
    """)

    # Also insert any PM names that exist in job.manager but not in project_manager yet
    op.execute("""
        INSERT INTO project_manager (name, is_active, display_order)
        SELECT DISTINCT TRIM(job.manager), true,
               COALESCE((SELECT MAX(display_order) FROM project_manager), 0) + 1
        FROM job
        WHERE job.manager IS NOT NULL
          AND job.manager_id IS NULL
          AND TRIM(job.manager) != ''
          AND NOT EXISTS (
              SELECT 1 FROM project_manager pm
              WHERE LOWER(TRIM(pm.name)) = LOWER(TRIM(job.manager))
          )
    """)

    # Now re-run the linkage for any newly inserted PMs
    op.execute("""
        UPDATE job
        SET manager_id = pm.id
        FROM project_manager pm
        WHERE job.manager_id IS NULL
          AND job.manager IS NOT NULL
          AND LOWER(TRIM(job.manager)) = LOWER(TRIM(pm.name))
    """)


def downgrade():
    # Nothing to undo - this is a data fix
    pass
