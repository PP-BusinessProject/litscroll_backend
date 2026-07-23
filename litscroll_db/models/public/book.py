from typing import TYPE_CHECKING, ClassVar, List, Optional

from sqlalchemy.orm import relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import (
    Integer,
    LargeBinary,
    SmallInteger,
    String,
)

from .._mixins import Timestamped
from ..base import Base, Permissions, Policies, TableArgs


if TYPE_CHECKING:
    from .book_quote import BookQuote
    from .book_genre import BookGenre
    from .book_excerpt_analysis import BookExcerptAnalysis


class Book(Timestamped, Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    title: Mapped[str] = Column(String(256), nullable=False)
    description: Mapped[str | None] = Column(String(1024))
    author_name: Mapped[str] = Column(String(128), nullable=False)
    year: Mapped[int] = Column(SmallInteger, nullable=False)
    page_count: Mapped[int] = Column(SmallInteger, nullable=False)
    image: Mapped[Optional[bytes]] = Column(LargeBinary)

    genres: Mapped[List['BookGenre']] = relationship(
        back_populates='book',
        lazy='noload',
        cascade='save-update, merge, expunge, delete, delete-orphan',
    )
    quotes: Mapped[List['BookQuote']] = relationship(
        back_populates='book',
        lazy='noload',
        cascade='save-update, merge, expunge, delete, delete-orphan',
    )
    excerpt_analyses: Mapped[list['BookExcerptAnalysis']] = relationship(
        back_populates='book',
        lazy='noload',
        cascade='all, delete-orphan',
    )

    __permissions__: ClassVar[Permissions] = dict(
        anon=dict(select=()),
        authenticated=dict(select=()),
    )
    __policies__: ClassVar[Policies] = dict(
        select_public=dict(command='select'),
    )

    __table_args__: ClassVar[TableArgs] = (
        dict(schema='public', comment='Books information table.'),
    )
