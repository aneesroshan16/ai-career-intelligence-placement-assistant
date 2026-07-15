import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Ensure every module's models are imported so Base.metadata is complete
# before autogenerate diffs the schema.
from app.core.config import get_settings
from app.core.database import Base
from app.modules.ats import models as _ats_models  # noqa: F401
from app.modules.aptitude import models as _aptitude_models  # noqa: F401
from app.modules.coding import models as _coding_models  # noqa: F401
from app.modules.interview import models as _interview_models  # noqa: F401
from app.modules.jobs import models as _jobs_models  # noqa: F401
from app.modules.matching import models as _matching_models  # noqa: F401
from app.modules.placement import models as _placement_models  # noqa: F401
from app.modules.readiness import models as _readiness_models  # noqa: F401
from app.modules.resumes import models as _resumes_models  # noqa: F401
from app.modules.roadmap import models as _roadmap_models  # noqa: F401
from app.modules.skills import models as _skills_models  # noqa: F401
from app.modules.users import models as _users_models  # noqa: F401

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
