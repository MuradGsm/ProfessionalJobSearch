from logging.config import fileConfig
import asyncio
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import Connection
from sqlalchemy import pool
import sys
from os.path import dirname, abspath
from alembic import context
from app.config.setting import settings

# Import all models for auto-generation
from app.models.users_model import User
from app.models.company_model import Company, CompanyMember, Invitation
from app.models.jobs_model import Job, Categories, Skill, Tag
from app.models.aplications_model import Application
from app.models.resumes_model import Resume
from app.models.messages_model import Message
from app.models.notifications_model import Notification
from app.models.prod_models import AuditLog, RateLimit, PerformanceMetric, CacheEntry, SchemaVersion

from app.db.database import Base

config = context.config
sys.path.insert(0, dirname(dirname(abspath(__file__))))

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata



def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()