from typing import ClassVar, Self, Type

from sqlalchemy.orm import relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.schema import Column, ForeignKey, Index

from litscroll_db.utils.descriptors import cachedclassproperty

from .._mixins import Timestamped
from ..base import Base, Permissions, Policies, TableArgs
from .book import Book
from .genre import Genre


class BookGenre(Timestamped, Base):
    book_id: Mapped[int] = Column(
        ForeignKey(Book.id, onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True,
    )
    genre_id: Mapped[int] = Column(
        ForeignKey(Genre.id, onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True,
    )

    book: Mapped[Book] = relationship(
        back_populates='genres',
        lazy='noload',
        cascade='save-update',
    )
    genre: Mapped[Genre] = relationship(
        back_populates='books',
        lazy='noload',
        cascade='save-update',
    )

    __permissions__: ClassVar[Permissions] = Book.__permissions__
    __policies__: ClassVar[Policies] = Book.__policies__

    @cachedclassproperty
    def __table_args__(cls: Type[Self], /) -> TableArgs:
        return (
            Index(None, cls.genre_id, cls.book_id),
            dict(schema='public', comment='Book genres.'),
        )
