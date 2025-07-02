# fix_notes_column.py
from app import app, db
from sqlalchemy import text

with app.app_context():
    # 1) Add the notes column if it isn't there already
    db.session.execute(text("""
        ALTER TABLE request
        ADD COLUMN IF NOT EXISTS notes TEXT;
    """))

    # 2) Stamp Alembic so it thinks your '8bac7ba2c203' migration is applied
    db.session.execute(text("""
        INSERT INTO alembic_version (version_num)
        SELECT '8bac7ba2c203'
          WHERE NOT EXISTS (
            SELECT 1
              FROM alembic_version
             WHERE version_num = '8bac7ba2c203'
          );
    """))

    db.session.commit()
    print("✅ Added notes column (if needed) and stamped alembic_version.")
