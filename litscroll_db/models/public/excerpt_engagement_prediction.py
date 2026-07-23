from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .book_excerpt_analysis import BookExcerptAnalysis


if TYPE_CHECKING:
    from .book_excerpt_analysis import BookExcerptAnalysis


class ExcerptEngagementPrediction(Base):
    __tablename__ = 'excerpt_engagement_prediction'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey(
            BookExcerptAnalysis.id,
            ondelete='CASCADE',
        ),
        nullable=False,
        unique=True,
    )

    stop_scroll_probability: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    finish_probability: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    like_probability: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    save_probability: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    share_probability: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    continue_book_probability: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    reread_probability: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    analysis: Mapped['BookExcerptAnalysis'] = relationship(
        back_populates='engagement_prediction',
    )

    __table_args__ = (
        CheckConstraint(
            'stop_scroll_probability BETWEEN 0 AND 1',
            name='ck_engagement_stop_scroll_probability',
        ),
        CheckConstraint(
            'finish_probability BETWEEN 0 AND 1',
            name='ck_engagement_finish_probability',
        ),
        CheckConstraint(
            'like_probability BETWEEN 0 AND 1',
            name='ck_engagement_like_probability',
        ),
        CheckConstraint(
            'save_probability BETWEEN 0 AND 1',
            name='ck_engagement_save_probability',
        ),
        CheckConstraint(
            'share_probability BETWEEN 0 AND 1',
            name='ck_engagement_share_probability',
        ),
        CheckConstraint(
            'continue_book_probability BETWEEN 0 AND 1',
            name='ck_engagement_continue_book_probability',
        ),
        CheckConstraint(
            'reread_probability BETWEEN 0 AND 1',
            name='ck_engagement_reread_probability',
        ),
    )
