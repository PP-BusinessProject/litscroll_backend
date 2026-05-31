from datetime import datetime
from typing import ClassVar, Optional, Self, Type

from sqlalchemy.orm import relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.schema import CheckConstraint, Column, ForeignKey, Index
from sqlalchemy.sql.sqltypes import DateTime, SmallInteger

from ...utils.descriptors import cachedclassproperty
from .._mixins import Timestamped
from ..auth.user import User
from ..base import Base, Events, Permissions, Policies, TableArgs
from .book_quote import BookQuote


class BookQuoteUser(Timestamped, Base):
    quote_id: Mapped[int] = Column(
        ForeignKey(BookQuote.id, onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True,
    )
    user_id: Mapped[int] = Column(
        ForeignKey(User.id, onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True,
    )
    progress: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint('progress >= 0 AND progress <= 100'),
        nullable=False,
        default=0,
    )
    finished_at: Mapped[Optional[datetime]] = Column(DateTime(), index=True)
    liked_at: Mapped[Optional[datetime]] = Column(DateTime(), index=True)

    quote: Mapped[BookQuote] = relationship(
        back_populates='users',
        lazy='noload',
        cascade='save-update',
    )
    user: Mapped[User] = relationship(
        back_populates='book_quotes',
        lazy='noload',
        cascade='save-update',
    )

    __permissions__: ClassVar[Permissions] = dict(
        authenticated=dict(select=(), insert=()),
    )
    __policies__: ClassVar[Policies] = dict(
        select_self=dict(
            roles='authenticated',
            command='select',
            using='auth.uid() = user_id',
        ),
        insert_self=dict(
            roles='authenticated',
            command='insert',
            with_check='auth.uid() = user_id',
        ),
        update_self=dict(
            roles='authenticated',
            command='update',
            with_check='auth.uid() = user_id',
        ),
    )

    @cachedclassproperty
    def __table_args__(cls: Type[Self], /) -> TableArgs:
        return (
            Index(None, cls.user_id, cls.liked_at),
            dict(schema='public', comment='Book quotes user data table.'),
        )

    @cachedclassproperty
    def __events__(cls: Type[Self], /) -> Events:
        return dict(
            after_create=cls.trigger(
                'book_quote_statistics',
                delete=True,
                body=f"""
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.{cls.liked_at.key} IS NOT NULL THEN
            UPDATE {BookQuote.__tablename__}
            SET {BookQuote.like_count.key} = {BookQuote.like_count.key} + 1
            WHERE {BookQuote.id.key} = NEW.{cls.quote_id.key};
        END IF;

        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.{cls.liked_at.key} IS NULL AND
          NEW.{cls.liked_at.key} IS NOT NULL THEN
            UPDATE {BookQuote.__tablename__}
            SET {BookQuote.like_count.key} = {BookQuote.like_count.key} + 1
            WHERE {BookQuote.id.key} = NEW.{cls.quote_id.key};
        ELSIF OLD.{cls.liked_at.key} IS NOT NULL AND
          NEW.{cls.liked_at.key} IS NULL THEN
            UPDATE {BookQuote.__tablename__}
            SET {BookQuote.like_count.key} = {BookQuote.like_count.key} - 1
            WHERE {BookQuote.id.key} = NEW.{cls.quote_id.key};
        END IF;

        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.{cls.liked_at.key} IS NOT NULL THEN
            UPDATE {BookQuote.__tablename__}
            SET {BookQuote.like_count.key} = {BookQuote.like_count.key} - 1
            WHERE {BookQuote.id.key} = OLD.{cls.quote_id.key};
        END IF;

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
""",
            )
        )
