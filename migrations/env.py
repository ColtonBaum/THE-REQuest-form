from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# this one points at the [alembic] section of alembic.ini
config = context.config

# set up Python logging via the config file
fileConfig(config.config_file_name)

# if you have Model.metadata to target, import it here:
# from public import db
# target_metadata = db.metadata
target_metadata = None


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
