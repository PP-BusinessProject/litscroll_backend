"""
Initial data.

Revision ID: 685447310e1b
Revises: 385949d9c34e
Create Date: 2022-09-20 11:17:44.303059+03:00
"""

from alembic.context import is_offline_mode
from alembic.op import get_bind
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.sql.ddl import DDL

from litscroll_db.models.base import Base


# revision identifiers, used by Alembic.
revision = 'initial_data'
down_revision = 'initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    def upgrade(session: Session, /) -> None:
        model: Base
        for name, model in Base._sa_registry._class_registry.items():
            if name.startswith('_'):
                continue
            for instance in model.__instances__ or ():
                session.add(instance)

    if is_offline_mode():
        upgrade(sessionmaker(get_bind())())
    else:
        with sessionmaker(get_bind())() as session:
            upgrade(session)
            session.commit()


def downgrade() -> None:
    with sessionmaker(get_bind())() as session:
        for table in reversed(Base.metadata.sorted_tables):
            if table.name.startswith('view'):
                continue
            table_name = (
                f'"{table.schema}"."{table.name}"'
                if table.schema
                else f'"{table.name}"'
            )
            session.execute(
                DDL(f"""
                DO $$
                BEGIN
                    IF to_regclass('{table_name.replace('"', '')}') IS NOT NULL THEN
                        EXECUTE 'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE';
                    END IF;
                END $$;
            """)
            )
