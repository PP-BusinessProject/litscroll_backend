from asyncio import run
from logging import getLogger
from os import environ
from sys import path
from typing import Union
from uuid import uuid4

from alembic.context import (
    begin_transaction,
    config,
    configure,
    is_offline_mode,
    run_migrations,
)
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.engine.create import engine_from_config
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool.impl import AsyncAdaptedQueuePool

from litscroll_db.models.base import Base


#
path.append('..')
MockConnection.close = lambda self: None


def do_run_migrations(connection: Union[str, Connection], /) -> None:
    configure(
        target_metadata=Base.metadata,
        literal_binds=not isinstance(connection, Connection),
        include_schemas=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts=dict(paramstyle='named'),
        include_name=lambda name, type_, _: (
            type_ == 'schema' and name in {'auth', 'public'}
        ),
        **{'url' if isinstance(connection, str) else 'connection': connection},
    )

    with begin_transaction():
        try:
            run_migrations()
        except* AttributeError as e:
            if isinstance(e.exceptions[0], MockConnection):
                raise e.exceptions[1]
            raise


async def do_run_migrations_async(engine: Engine, /) -> None:
    async with (engine := AsyncEngine(engine)).connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though an
    Engine is acceptable here as well. By skipping the Engine creation we don't
    even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    if (url := config.get_main_option('sqlalchemy.url')) in environ:
        url = environ[url]
    do_run_migrations('postgresql+asyncpg://' + url.split('://', 1)[-1])


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    sync_engine = engine_from_config(
        cfg := config.get_section(config.config_ini_section)
    )
    getLogger('sqlalchemy.engine.Engine').propagate = False
    if sync_engine.dialect.is_async:
        from asyncpg import Connection

        class CustomConnection(Connection):
            def _get_unique_id(self, prefix: str) -> str:
                return f'__asyncpg_{prefix}_{uuid4()}__'

        engine = engine_from_config(
            cfg,
            future=True,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=1,
            max_overflow=-1,
            pool_recycle=3600,
            pool_pre_ping=True,
            pool_use_lifo=True,
            connect_args=dict(
                ssl=False,
                server_settings=dict(jit='off'),
                statement_cache_size=0,
                prepared_statement_cache_size=0,
                connection_class=CustomConnection,
            ),
        )
        run(do_run_migrations_async(engine))
    else:
        with sync_engine.begin() as connection:
            do_run_migrations(connection)


if is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
