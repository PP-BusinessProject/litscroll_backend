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


class ExcerptStyleAnalysis(Base):
    __tablename__ = 'excerpt_style_analysis'

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

    dialogue_ratio: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'dialogue_ratio BETWEEN 0 AND 100',
            name='ck_style_dialogue_ratio',
        ),
        nullable=False,
    )

    description_ratio: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'description_ratio BETWEEN 0 AND 100',
            name='ck_style_description_ratio',
        ),
        nullable=False,
    )

    action_ratio: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'action_ratio BETWEEN 0 AND 100',
            name='ck_style_action_ratio',
        ),
        nullable=False,
    )

    reflection_ratio: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'reflection_ratio BETWEEN 0 AND 100',
            name='ck_style_reflection_ratio',
        ),
        nullable=False,
    )

    reading_difficulty: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'reading_difficulty BETWEEN 0 AND 100',
            name='ck_style_reading_difficulty',
        ),
        nullable=False,
    )

    context_required: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'context_required BETWEEN 0 AND 100',
            name='ck_style_context_required',
        ),
        nullable=False,
    )

    works_without_context: Mapped[Decimal] = Column(
        Numeric(5, 2),
        CheckConstraint(
            'works_without_context BETWEEN 0 AND 100',
            name='ck_style_works_without_context',
        ),
        nullable=False,
    )

    quote: Mapped['BookQuote'] = relationship(
        back_populates='style_analysis',
    )
