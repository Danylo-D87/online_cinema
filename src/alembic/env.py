import asyncio
from sqlalchemy.engine import Connection
from alembic import context

from src.database.setup import engine
from src.database.base import Base
from src.models import *


config = context.config

target_metadata = Base.metadata


def run_migrations_offline() -> None:
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
    connectable = engine

    async with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            dialect_name=connection.dialect.name
        )
        await connection.run_sync(do_run_migrations)


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
