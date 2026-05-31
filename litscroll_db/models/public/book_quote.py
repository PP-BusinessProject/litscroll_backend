from typing import TYPE_CHECKING, ClassVar, List, Self, Type

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.schema import CheckConstraint, Column, ForeignKey, Index
from sqlalchemy.sql.sqltypes import (
    Integer,
    String,
)

from litscroll_db.utils.descriptors import cachedclassproperty

from .._mixins import Timestamped
from ..base import Base, Permissions, Policies, TableArgs
from .book import Book


if TYPE_CHECKING:
    from .book_quote_user import BookQuoteUser


class BookQuote(Timestamped, Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    book_id: Mapped[int] = Column(
        ForeignKey(Book.id, onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    like_count: Mapped[int] = Column(
        Integer,
        CheckConstraint('like_count > 0'),
        nullable=False,
        default=0,
    )
    paragraphs: Mapped[list[str]] = Column(
        ARRAY(String(1024)),
        nullable=False,
        default=[],
    )

    book: Mapped[Book] = relationship(
        back_populates='quotes',
        lazy='noload',
        cascade='save-update',
    )

    users: Mapped[List['BookQuoteUser']] = relationship(
        back_populates='quote',
        lazy='noload',
        cascade='save-update, merge, expunge, delete, delete-orphan',
    )

    __permissions__: ClassVar[Permissions] = Book.__permissions__
    __policies__: ClassVar[Policies] = Book.__policies__

    @cachedclassproperty
    def __table_args__(cls: Type[Self], /) -> TableArgs:
        return (
            Index(None, cls.like_count.desc()),
            dict(schema='public', comment='Book quotes table.'),
        )
