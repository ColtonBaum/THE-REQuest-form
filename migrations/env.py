from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# this line may already be there — just add your import:
from models import db

# …

# tell Alembic to use your models’ metadata
target_metadata = db.metadata

# … the rest should stay as generated
