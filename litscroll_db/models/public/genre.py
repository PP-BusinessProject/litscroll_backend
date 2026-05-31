from typing import TYPE_CHECKING, ClassVar, List

from sqlalchemy.orm import relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import (
    SmallInteger,
    String,
)

from .._mixins import Timestamped
from ..base import Base, Permissions, Policies, TableArgs


if TYPE_CHECKING:
    from .book_genre import BookGenre


class Genre(Timestamped, Base):
    id: Mapped[int] = Column(SmallInteger, primary_key=True)
    name: Mapped[str] = Column(String(256), nullable=False)

    books: Mapped[List['BookGenre']] = relationship(
        back_populates='genre',
        lazy='noload',
        cascade='save-update, merge, expunge, delete, delete-orphan',
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
