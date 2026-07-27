from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql.schema import Column

from ..base import Base
from .book_quote import BookQuote


if TYPE_CHECKING:
    from .book_quote import BookQuote


class BookQuoteEngagementPrediction(Base):
    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
    )

    quote_id: Mapped[int] = Column(
        ForeignKey(
            BookQuote.id,
            ondelete='CASCADE',
        ),
        nullable=False,
        unique=True,
    )

    stop_scroll_probability: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'stop_scroll_probability BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    finish_probability: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'finish_probability BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    like_probability: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'like_probability BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    save_probability: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'save_probability BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    share_probability: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'share_probability BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    continue_book_probability: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'continue_book_probability BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    reread_probability: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'reread_probability BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    quote: Mapped['BookQuote'] = relationship(
        back_populates='engagement_prediction',
        lazy='noload',
        cascade='save-update',
    )
