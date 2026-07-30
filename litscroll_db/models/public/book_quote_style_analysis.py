from __future__ import annotations


from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql.schema import Column

from ..base import Base
from .book_quote import BookQuote


if TYPE_CHECKING:
    from .book_quote import BookQuote


class BookQuoteStyleAnalysis(Base):
    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
    )

    quote_id: Mapped[int] = Column(
        ForeignKey(
            BookQuote.id,
            onupdate='CASCADE',
            ondelete='CASCADE',
        ),
        nullable=False,
        unique=True,
    )

    dialogue_ratio: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'dialogue_ratio BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    description_ratio: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'description_ratio BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    action_ratio: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'action_ratio BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    reflection_ratio: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'reflection_ratio BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    reading_difficulty: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'reading_difficulty BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    context_required: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'context_required BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    works_without_context: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'works_without_context BETWEEN 0 AND 100',
        ),
        nullable=False,
    )

    quote: Mapped[BookQuote] = relationship(
        back_populates='style_analysis',
        lazy='noload',
        cascade='save-update',
    )
