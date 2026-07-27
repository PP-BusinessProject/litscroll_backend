from typing import TYPE_CHECKING, Any, ClassVar, List, Self, Type

from sqlalchemy.dialects.postgresql import ARRAY, JSONB
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
    from .excerpt_engagement_prediction import (
        ExcerptEngagementPrediction,
    )
    from .excerpt_narrative import ExcerptNarrative
    from .excerpt_ranking import ExcerptRanking
    from .excerpt_style_analysis import ExcerptStyleAnalysis
    from .book_quote_user import BookQuoteUser


class BookQuote(Timestamped, Base):
    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
    )

    book_id: Mapped[int] = Column(
        ForeignKey(
            Book.id,
            onupdate='CASCADE',
            ondelete='CASCADE',
        ),
        nullable=False,
        index=True,
    )

    like_count: Mapped[int] = Column(
        Integer,
        CheckConstraint(
            'like_count >= 0',
            name='ck_book_quote_like_count',
        ),
        nullable=False,
        default=0,
    )

    embedding_summary: Mapped[str] = Column(
        String(1000),
        nullable=False,
    )

    excerpt_text: Mapped[list[list[str]]] = Column(
        JSONB,
        nullable=False,
    )

    word_count: Mapped[int] = Column(
        Integer,
        CheckConstraint(
            'word_count >= 0',
            name='ck_book_quote_word_count',
        ),
        nullable=False,
    )

    summary: Mapped[str] = Column(
        String(2000),
        nullable=False,
    )

    opening_hook: Mapped[str] = Column(
        String(1000),
        nullable=False,
    )

    best_quote: Mapped[str] = Column(
        String(2000),
        nullable=False,
    )

    one_sentence_pitch: Mapped[str] = Column(
        String(500),
        nullable=False,
    )

    themes: Mapped[list[str]] = Column(
        ARRAY(String(100)),
        nullable=False,
        default=list,
    )

    keywords: Mapped[list[str]] = Column(
        ARRAY(String(100)),
        nullable=False,
        default=list,
    )

    observations: Mapped[dict[str, list[Any]]] = Column(
        JSONB,
        nullable=False,
        default=dict,
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

    ranking: Mapped['ExcerptRanking'] = relationship(
        back_populates='quote',
        lazy='noload',
        uselist=False,
        cascade='save-update, merge, expunge, delete, delete-orphan',
    )

    narrative: Mapped['ExcerptNarrative'] = relationship(
        back_populates='quote',
        lazy='noload',
        uselist=False,
        cascade='save-update, merge, expunge, delete, delete-orphan',
    )

    style_analysis: Mapped['ExcerptStyleAnalysis'] = relationship(
        back_populates='quote',
        lazy='noload',
        uselist=False,
        cascade='save-update, merge, expunge, delete, delete-orphan',
    )

    engagement_prediction: Mapped['ExcerptEngagementPrediction'] = (
        relationship(
            back_populates='quote',
            lazy='noload',
            uselist=False,
            cascade='save-update, merge, expunge, delete, delete-orphan',
        )
    )

    __permissions__: ClassVar[Permissions] = Book.__permissions__
    __policies__: ClassVar[Policies] = Book.__policies__

    @cachedclassproperty
    def __table_args__(cls: Type[Self], /) -> TableArgs:
        return (
            Index(None, cls.like_count.desc()),
            dict(
                schema='public',
                comment='Book quotes table.',
            ),
        )
