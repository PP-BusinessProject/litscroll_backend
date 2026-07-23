from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .book_excerpt_analysis import BookExcerptAnalysis

if TYPE_CHECKING:
    from .book_excerpt_analysis import BookExcerptAnalysis


class ExcerptStyleAnalysis(Base):
    __tablename__ = 'excerpt_style_analysis'

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

    dialogue_ratio: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    description_ratio: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    action_ratio: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    reflection_ratio: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    reading_difficulty: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    context_required: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    works_without_context: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )

    analysis: Mapped['BookExcerptAnalysis'] = relationship(
        back_populates='style_analysis',
    )

    __table_args__ = (
        CheckConstraint(
            'dialogue_ratio BETWEEN 0 AND 1',
            name='ck_style_dialogue_ratio',
        ),
        CheckConstraint(
            'description_ratio BETWEEN 0 AND 1',
            name='ck_style_description_ratio',
        ),
        CheckConstraint(
            'action_ratio BETWEEN 0 AND 1',
            name='ck_style_action_ratio',
        ),
        CheckConstraint(
            'reflection_ratio BETWEEN 0 AND 1',
            name='ck_style_reflection_ratio',
        ),
        CheckConstraint(
            'reading_difficulty BETWEEN 0 AND 1',
            name='ck_style_reading_difficulty',
        ),
        CheckConstraint(
            'context_required BETWEEN 0 AND 1',
            name='ck_style_context_required',
        ),
        CheckConstraint(
            'works_without_context BETWEEN 0 AND 1',
            name='ck_style_works_without_context',
        ),
    )
