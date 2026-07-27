from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql.schema import Column

from ..base import Base
from .book_quote import BookQuote

if TYPE_CHECKING:
    from .book_quote import BookQuote


class ExcerptEngagementPrediction(Base):
    __tablename__ = 'excerpt_engagement_prediction'

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

    stop_scroll_probability: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'stop_scroll_probability BETWEEN 0 AND 100',
            name='ck_engagement_stop_scroll_probability',
        ),
        nullable=False,
    )

    finish_probability: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'finish_probability BETWEEN 0 AND 100',
            name='ck_engagement_finish_probability',
        ),
        nullable=False,
    )

    like_probability: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'like_probability BETWEEN 0 AND 100',
            name='ck_engagement_like_probability',
        ),
        nullable=False,
    )

    save_probability: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'save_probability BETWEEN 0 AND 100',
            name='ck_engagement_save_probability',
        ),
        nullable=False,
    )

    share_probability: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'share_probability BETWEEN 0 AND 100',
            name='ck_engagement_share_probability',
        ),
        nullable=False,
    )

    continue_book_probability: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'continue_book_probability BETWEEN 0 AND 100',
            name='ck_engagement_continue_book_probability',
        ),
        nullable=False,
    )

    reread_probability: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'reread_probability BETWEEN 0 AND 100',
            name='ck_engagement_reread_probability',
        ),
        nullable=False,
    )

    quote: Mapped['BookQuote'] = relationship(
        back_populates='engagement_prediction',
    )
