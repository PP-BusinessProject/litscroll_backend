from logging import basicConfig
from os.path import abspath, basename, dirname

from alembic.command import downgrade, upgrade
from alembic.config import Config
from click import command, option


@command(
    context_settings=dict(token_normalize_func=lambda x: x.strip().lower()),
)
@option(
    '-l',
    '--logging',
    help='The *logging* level used to display messges.',
    default='INFO',
    callback=lambda ctx, param, value: value.strip().upper(),
)
@option(
    '-d',
    '--database-url',
    help='The *database_url* to use with SQLAlchemy.',
    required=True,
    envvar=['DATABASE_URL'],
    callback=lambda ctx, param, value: (
        'postgresql+asyncpg://' + value.split('://')[-1].split('?')[0].strip()
        if value
        else None
    ),
)
@option(
    '--sql',
    help='If run the script in offline mode.',
    envvar=['SQL'],
    is_flag=True,
)
def cli(
    logging: str,
    database_url: str,
    sql: bool,
) -> None:
    basicConfig(level=logging, force=True)
    alembic_cfg = Config()
    alembic_cfg.set_main_option(
        'script_location',
        basename(dirname(abspath(__file__))),
    )
    alembic_cfg.set_main_option('sqlalchemy.echo', 'true')
    alembic_cfg.set_main_option('sqlalchemy.url', database_url)
    if not sql:
        downgrade(alembic_cfg, 'base', sql=sql)
    upgrade(alembic_cfg, 'initial', sql=sql)
    upgrade(alembic_cfg, 'head', sql=sql)


if __name__ == '__main__':
    cli()
