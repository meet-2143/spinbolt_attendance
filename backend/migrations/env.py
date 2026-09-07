from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.config import get_settings
from app.database.session import Base
from app.models import Attendance, AuditLog, User  # noqa: F401  (registers metadata)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

settings = get_settings()
# Migrations always run against the direct (non-pooled) connection string, even
# when the app itself talks to Supabase through the Supavisor pooler. Built and
# used directly (not via config.set_main_option/get_section) because a
# percent-encoded password (e.g. "%40") collides with configparser's own
# interpolation syntax otherwise.
db_url = settings.database_url_direct_normalized or settings.database_url_normalized


def run_migrations_offline() -> None:
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(db_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
