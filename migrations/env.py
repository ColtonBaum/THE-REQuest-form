import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# this is the Alembic Config object, based on alembic.ini
config = context.config

# set up Python logging per the ini file
fileConfig(config.config_file_name)

# if you have MetaData for autogenerate, import it here:
# from yourapp import db
# target_metadata = db.metadata
target_metadata = None

def get_url():
    return os.environ["DATABASE_URL"]

def run_migrations_offline():
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # override the ini file’s URL entirely with the one from env
    configuration = config.get_section(config.config_ini_section).copy()
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
