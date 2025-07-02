from public import db
from sqlalchemy import text

# fetch all columns on your request table
cols = db.engine.execute(text("""
    SELECT column_name, data_type
      FROM information_schema.columns
     WHERE table_name = 'request'
     ORDER BY ordinal_position
""")).fetchall()

print("Columns in request:")
for name, dtype in cols:
    print(f" • {name}  ({dtype})")
