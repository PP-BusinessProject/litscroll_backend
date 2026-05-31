from typing import TYPE_CHECKING, ClassVar, List
from uuid import UUID

from sqlalchemy.orm import Relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import UUID as sql_UUID

from ..base import Base, TableArgs


if TYPE_CHECKING:
    from ..public.books.book_quote_user import BookQuoteUser


class User(Base):
    id: Mapped[UUID] = Column(sql_UUID(), primary_key=True)

    book_quotes: Mapped[List['BookQuoteUser']] = Relationship(
        back_populates='user',
        lazy='noload',
        cascade='save-update, merge, expunge, delete, delete-orphan',
    )

    __table_args__: ClassVar[TableArgs] = (
        dict(schema='auth', comment='Placeholder to make foreign joins.'),
    )
