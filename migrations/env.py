# migrations/env.py
import os
import sys
from urllib.parse import urlparse

from alembic import context
from sqlalchemy import pool, create_engine

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from models import db  # must succeed

config = context.config
target_metadata = db.metadata


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")
    if not url:
        raise RuntimeError("DATABASE_URL is not set (required for migrations).")

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    p = urlparse(url)

    # ✅ Hard fail if anything tries to run migrations on SQLite
    if p.scheme.startswith("sqlite"):
        raise RuntimeError("Refusing to run migrations against SQLite. Set DATABASE_URL to Postgres.")

    # ✅ Log a *sanitized* connection target so you can confirm in DO logs
    safe = f"{p.scheme}://{p.hostname}:{p.port or ''}{p.path}"
    if p.query:
        safe += f"?{p.query}"
    print(f"[alembic] Using DB: {safe}", flush=True)

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
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
