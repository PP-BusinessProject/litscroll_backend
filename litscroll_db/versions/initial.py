"""
Initial.

Revision ID: 385949d9c34e
Revises: 6b7e152e969f
Create Date: 2022-09-20 09:35:30.065729+03:00
"""

from typing import Final, Iterable, List, Set

from alembic.context import get_context
from alembic.op import get_bind
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.event import listen
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import Column, DropTable
from sqlalchemy.sql.ddl import DDL
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.selectable import ClauseElement

from litscroll_db.models.base import Base, Permissions


# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None


@compiles(DropTable, 'postgresql')
def _compile_drop_table(element, compiler, **kwargs):
    """DROP TABLE ... CASCADE implementation for PostgreSQL dialect."""
    return compiler.visit_drop_table(element) + ' CASCADE'


SUPABASE_SCHEMAS: Final[Set[str]] = {
    'auth',
    'extensions',
    'graphql',
    'graphql_public',
    'pgsodium',
    'pgsodium_masks',
    'realtime',
    'storage',
    'supabase_migrations',
    'vault',
}


def _select_public_tables() -> Iterable[Table]:
    return (
        model.__table__
        for model in _select_public_models()
        if getattr(model, '__selectable__', None) is None
    )


def _select_public_models() -> Iterable[Base]:
    runs_linux = 'gcc' in get_bind().scalar(select(func.version()))
    return (
        model
        for name, model in Base._sa_registry._class_registry.items()
        if hasattr(model, '__table__')
        and (
            not runs_linux
            or (model.__table__.schema or 'public') not in SUPABASE_SCHEMAS
        )
        and model.__table__ is not get_context()._version
    )


def create_schema(schema: str, /) -> DDL:
    if schema == 'auth':
        return DDL("""DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE p.proname = 'uid'
            AND n.nspname = 'auth'
            AND p.pronargs = 0
    ) THEN
        CREATE SCHEMA IF NOT EXISTS auth;

        CREATE FUNCTION auth.uid()
        RETURNS uuid
        LANGUAGE sql
        STABLE
        AS $func$
        SELECT COALESCE(
            current_setting('request.jwt.claim.sub', true)::uuid,
            '00000000-0000-0000-0000-000000000001'::uuid
        );
        $func$;
    END IF;
END
$$;
""")

    return DDL(f'CREATE SCHEMA IF NOT EXISTS {schema}')


def drop_schema(schema: str, /) -> DDL:
    return DDL(f'DROP SCHEMA IF EXISTS {schema} CASCADE')


def create_extension(extension: str, /) -> DDL:
    return DDL(
        f'CREATE EXTENSION IF NOT EXISTS {extension} CASCADE'
    ).execute_if(dialect='postgresql')


def drop_extension(extension: str, /) -> DDL:
    return DDL(f'DROP EXTENSION IF EXISTS {extension} CASCADE').execute_if(
        dialect='postgresql'
    )


def grant_permissions(model: Base, /) -> Iterable[DDL]:
    permissions: Final[Permissions] = model.__permissions__ or {}
    return (
        _.execute_if(dialect='postgresql')
        for _ in (
            DDL(f'GRANT ALL ON TABLE {model.__table__.fullname} TO postgres'),
            *(
                DDL(
                    'GRANT {} '.format(
                        ', '.join(
                            _.upper()
                            for _ in (
                                (command,)
                                if isinstance(command, str)
                                else command
                            )
                        )
                        if isinstance(command, Iterable) and command
                        else 'ALL'
                    )
                    + (
                        '(%s) '
                        % ', '.join(
                            _ if isinstance(_, str) else _.name
                            for _ in (
                                columns
                                if isinstance(columns, Iterable)
                                and not isinstance(columns, str)
                                else (columns,)
                            )
                        )
                        if isinstance(columns, Column)
                        or isinstance(columns, Iterable)
                        and columns
                        else ''
                    )
                    + f'ON TABLE {model.__table__.fullname}'
                    + (
                        ' TO {}'.format(
                            role if isinstance(role, str) else ', '.join(role)
                        )
                        if isinstance(role, Iterable) and role
                        else ''
                    )
                )
                for role, commands in permissions.items()
                for command, columns in (commands or dict(all=())).items()
            ),
        )
        if _ is not None
    )


def revoke_permissions(model: Base, /) -> Iterable[DDL]:
    return (
        _.execute_if(dialect='postgresql')
        for _ in (
            DDL(
                f'REVOKE ALL ON TABLE {model.__table__.fullname} FROM postgres'
            ),
            *(
                DDL(
                    'REVOKE {} '.format(
                        ', '.join(
                            _.upper()
                            for _ in (
                                (command,)
                                if isinstance(command, str)
                                else command
                            )
                        )
                        if isinstance(command, Iterable) and command
                        else 'ALL'
                    )
                    + (
                        '(%s) '
                        % ', '.join(
                            _.name if isinstance(_, Column) else _
                            for _ in (
                                (columns,)
                                if isinstance(columns, (str, Column))
                                else columns
                            )
                        )
                        if isinstance(columns, Column)
                        or isinstance(columns, Iterable)
                        and columns
                        else ''
                    )
                    + f'ON TABLE {model.__table__.fullname}'
                    + (
                        ' FROM {}'.format(
                            role if isinstance(role, str) else ', '.join(role)
                        )
                        if isinstance(role, Iterable) and role
                        else ''
                    )
                )
                for role, commands in (model.__permissions__ or {}).items()
                for command, columns in (commands or dict(all=())).items()
            ),
        )
        if _ is not None
    )


def enable_rls(model: Base, /) -> DDL:
    return DDL(
        f'ALTER TABLE {model.__table__.fullname} ENABLE ROW LEVEL SECURITY'
    ).execute_if(dialect='postgresql')


def disable_rls(model: Base, /) -> DDL:
    return DDL(
        f'ALTER TABLE {model.__table__.fullname} DISABLE ROW LEVEL SECURITY'
    ).execute_if(dialect='postgresql')


def create_policies(model: Base, /) -> Iterable[DDL]:
    policies: Final[List[DDL]] = []
    for name, policy in (model.__policies__ or {}).items():
        if not name:
            continue

        command = policy.get('command')
        roles = policy.get('roles')
        using = policy.get('using')
        with_check = policy.get('with_check')
        policy = DDL(
            f'CREATE POLICY {name} ON {model.__table__.fullname} '
            + ('AS RESTRICTIVE ' if policy.get('restrictive') else '')
            + (f'FOR {command.upper()} ' if command else '')
            + 'TO {} '.format(
                (roles if isinstance(roles, str) else ', '.join(roles))
                if isinstance(roles, Iterable) and roles
                else 'PUBLIC'
            )
            + (
                'USING ({}) '.format(
                    using.compile(get_bind())
                    if isinstance(using, ClauseElement)
                    else using
                )
                if isinstance(using, ClauseElement) or using
                else (
                    'USING (true) '
                    if command is None
                    or command.upper() in {'ALL', 'SELECT', 'DELETE'}
                    else ''
                )
            )
            + (
                'WITH CHECK ({})'.format(
                    with_check.compile(get_bind())
                    if isinstance(with_check, ClauseElement)
                    else with_check
                )
                if isinstance(with_check, ClauseElement) or with_check
                else (
                    'WITH CHECK (true) '
                    if command is None
                    or command.upper() in {'INSERT', 'UPDATE'}
                    else ''
                )
            )
        ).execute_if(dialect='postgresql')
        policies.append(policy)

    return policies


def drop_policies(model: Base, /) -> Iterable[DDL]:
    return (
        DDL(
            f'DROP POLICY IF EXISTS {name} ON {model.__table__.fullname} '
            'CASCADE'
        ).execute_if(dialect='postgresql')
        for name, policy in (model.__policies__ or {}).items()
        if name
    )


def get_updated_at_trigger(model: Base, /) -> DDL:
    return DDL(
        f"""
CREATE OR REPLACE TRIGGER handle_updated_at BEFORE UPDATE ON {model.__table__.fullname}
FOR EACH ROW EXECUTE PROCEDURE moddatetime(updated_at)
"""
    ).execute_if(dialect='postgresql')


def get_materialized_refresh_trigger(model: Base, /) -> Iterable[DDL]:
    concurrently = ''
    if model.__is_materialized_concurrently__ in {None, True}:
        concurrently = ' CONCURRENTLY'
    return (
        DDL(_).execute_if('postgresql')
        for _ in dict.fromkeys(
            _
            for dependant_model in model.__is_materialized_depending_on__
            or (_.entity.class_ for _ in model.relationships)
            for _ in dependant_model.trigger(
                f'refresh_{model.__tablename__}',
                f"""
BEGIN
    REFRESH MATERIALIZED VIEW{concurrently} {model.__table__.fullname};
    RETURN NULL;
END;""",
                before=False,
                delete=True,
                scope='STATEMENT',
                comment='Refresh a materialized view after '
                f'`{model.__table__.fullname}` change.',
            )
        )
    )


def get_materialized_refresh_cron(model: Base, /) -> Iterable[DDL]:
    concurrently = ''
    if (
        model.__is_materialized_concurrently__ is None
        or model.__is_materialized_concurrently__
    ):
        concurrently = ' CONCURRENTLY'
    return (
        DDL(_).execute_if('postgresql')
        for _ in model.cron(
            f'refresh_{model.__table__.fullname.replace(".", "_")}',
            f'REFRESH MATERIALIZED VIEW{concurrently} {model.__table__.fullname}',
            model.__materialized_refresh_cron__,
        )
    )


def create_view(model: Base, /) -> DDL:
    return DDL(
        'CREATE {materialized} VIEW{check} {name} AS {body}'.format(
            name=model.__table__.fullname,
            materialized=(
                'MATERIALIZED' if model.__is_materialized__ else 'OR REPLACE'
            ),
            check=' IF NOT EXISTS' if model.__is_materialized__ else '',
            body=model.__selectable__.compile(
                get_bind(),
                compile_kwargs=dict(literal_binds=True),
            ),
        )
    ).execute_if(dialect='postgresql')


def drop_view(model: Base, /) -> DDL:
    return DDL(
        'DROP{materialized} VIEW IF EXISTS {name} CASCADE'.format(
            name=model.__table__.fullname,
            materialized=' MATERIALIZED' if model.__is_materialized__ else '',
        )
    ).execute_if(dialect='postgresql')


def upgrade() -> None:
    runs_linux = 'gcc' in get_bind().scalar(select(func.version()))
    extensions: set[str] = {'btree_gist', 'cube', 'earthdistance'}
    model: Base
    for role in {
        role
        for model in _select_public_models()
        for role in model.__permissions__ or {}
    }:
        listen(
            Base.metadata,
            'before_create',
            DDL(f"""DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = '{role}'
    ) THEN
        CREATE ROLE {role};
    END IF;
END
$$;"""),
        )

    for model in _select_public_models():
        if model.__tablename__.startswith('_'):
            continue
        for listenable, events in (model.__events__ or {}).items():
            for event in (
                events
                if isinstance(events, Iterable) and not isinstance(events, str)
                else (events,)
            ):
                listen(
                    Base.metadata,
                    listenable,
                    DDL(event) if isinstance(event, str) else event,
                )
        if model.__selectable__ is not None:
            print(model)
            listen(Base.metadata, 'after_create', create_view(model))
            if model.__is_materialized__:
                if model.__materialized_refresh_cron__ and runs_linux:
                    extensions.add('pg_cron')
                    for ddl in get_materialized_refresh_cron(model):
                        listen(Base.metadata, 'after_create', ddl)
                else:
                    for ddl in get_materialized_refresh_trigger(model):
                        listen(Base.metadata, 'after_create', ddl)

        for permission in grant_permissions(model):
            listen(Base.metadata, 'after_create', permission)
        if policies := create_policies(model):
            listen(Base.metadata, 'after_create', enable_rls(model))
            for policy in policies:
                listen(Base.metadata, 'after_create', policy)
        table = model.__table__
        if 'updated_at' in table.columns:
            listen(table, 'after_create', get_updated_at_trigger(model))
            extensions.add('moddatetime')
        if ('pgcrypto' not in extensions and table.schema == 'public') and any(
            isinstance(column.type, UUID) and column.server_default is not None
            for column in table.columns
        ):
            extensions.add('pgcrypto')
    for schema in {t.schema or 'public' for t in _select_public_tables()}:
        listen(Base.metadata, 'before_create', create_schema(schema))
    for extension in extensions:
        listen(Base.metadata, 'before_create', create_extension(extension))
    listen(Base.metadata, 'after_create', DDL("NOTIFY pgrst, 'reload schema'"))
    Base.metadata.create_all(get_bind(), tables=_select_public_tables())


def downgrade() -> None:
    runs_linux = 'gcc' in get_bind().scalar(select(func.version()))
    extensions: set[str] = {'btree_gist', 'cube', 'earthdistance'}
    for model in _select_public_models():
        if model.__tablename__.startswith('_'):
            continue
        table: Table = model.__table__
        if model.__selectable__ is not None:
            listen(Base.metadata, 'before_drop', drop_view(model))
            if model.__is_materialized__:
                if model.__materialized_refresh_cron__ and runs_linux:
                    extensions.add('pg_cron')
        if 'updated_at' in table.columns:
            extensions.add('moddatetime')
        if ('pgcrypto' not in extensions and table.schema == 'public') and any(
            isinstance(column.type, UUID) and column.server_default is not None
            for column in table.columns
        ):
            extensions.add('pgcrypto')
    for extension in extensions:
        listen(Base.metadata, 'after_drop', drop_extension(extension))
    for schema in {t.schema for t in _select_public_tables()}:
        if schema != 'public':
            listen(Base.metadata, 'after_drop', drop_schema(schema))
    Base.metadata.drop_all(get_bind(), tables=_select_public_tables())
