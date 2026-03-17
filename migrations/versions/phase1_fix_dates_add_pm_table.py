"""phase 1 – convert need_by_date to DATE; add project_manager table"""

from alembic import op
import sqlalchemy as sa

revision = 'd1e2f3a4b5c6'
down_revision = '566afd622dd2'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        return

    # 1. Create project_manager table
    op.create_table(
        'project_manager',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # 2. Add manager_id FK to job
    op.add_column('job', sa.Column('manager_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_job_manager_id', 'job', 'project_manager', ['manager_id'], ['id']
    )

    # 3. Make job.manager nullable (was NOT NULL in baseline)
    op.alter_column('job', 'manager', nullable=True)

    # 4. NULL out any need_by_date values that aren't valid YYYY-MM-DD
    op.execute(
        "UPDATE request "
        "SET need_by_date = NULL "
        "WHERE need_by_date !~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'"
    )

    # 5. Convert need_by_date from VARCHAR(50) NOT NULL to DATE NULL
    op.execute(
        "ALTER TABLE request "
        "ALTER COLUMN need_by_date TYPE DATE USING need_by_date::date"
    )
    op.execute("ALTER TABLE request ALTER COLUMN need_by_date DROP NOT NULL")


def downgrade():
    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        return

    # Reverse need_by_date back to VARCHAR(50) NOT NULL
    op.execute(
        "ALTER TABLE request "
        "ALTER COLUMN need_by_date TYPE VARCHAR(50) "
        "USING COALESCE(need_by_date::text, '')"
    )
    op.execute("ALTER TABLE request ALTER COLUMN need_by_date SET NOT NULL")

    # Restore job.manager to NOT NULL (fill NULLs first)
    op.execute("UPDATE job SET manager = '' WHERE manager IS NULL")
    op.alter_column('job', 'manager', nullable=False)

    # Drop manager_id FK and column
    op.drop_constraint('fk_job_manager_id', 'job', type_='foreignkey')
    op.drop_column('job', 'manager_id')

    # Drop project_manager table
    op.drop_table('project_manager')
