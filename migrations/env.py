# migrations/env.py
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, create_engine

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from models import db  # must succeed

config = context.config

# ✅ Only load logging config if the referenced ini file actually exists
if config.config_file_name and os.path.exists(config.config_file_name):
    fileConfig(config.config_file_name)

target_metadata = db.metadata


def get_database_url() -> str:
    # Prefer env vars so prod never accidentally migrates SQLite
    url = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")

    # Fallback to alembic.ini only for local/dev convenience
    if not url:
        url = config.get_main_option("sqlalchemy.url")

    if not url:
        raise RuntimeError("No database URL found. Set DATABASE_URL in the environment.")

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    return url


def run_migrations_offline() -> None:
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_database_url()
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
