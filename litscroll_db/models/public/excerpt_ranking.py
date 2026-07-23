from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .book_excerpt_analysis import BookExcerptAnalysis

if TYPE_CHECKING:
    from .book_excerpt_analysis import BookExcerptAnalysis


class ExcerptRanking(Base):
    __tablename__ = 'excerpt_ranking'

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

    overall_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    hook_strength: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    continue_reading_pressure: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    curiosity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    suspense: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    emotional_intensity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    beauty_of_writing: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    thought_provoking: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    viral_potential: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    shareability: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    memorability: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    quotation_potential: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    discussion_potential: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    analysis: Mapped['BookExcerptAnalysis'] = relationship(
        back_populates='ranking',
    )

    __table_args__ = (
        CheckConstraint(
            'overall_score BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_overall_score',
        ),
        CheckConstraint(
            'hook_strength BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_hook_strength',
        ),
        CheckConstraint(
            'continue_reading_pressure BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_continue_reading_pressure',
        ),
        CheckConstraint(
            'curiosity BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_curiosity',
        ),
        CheckConstraint(
            'suspense BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_suspense',
        ),
        CheckConstraint(
            'emotional_intensity BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_emotional_intensity',
        ),
        CheckConstraint(
            'beauty_of_writing BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_beauty_of_writing',
        ),
        CheckConstraint(
            'thought_provoking BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_thought_provoking',
        ),
        CheckConstraint(
            'viral_potential BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_viral_potential',
        ),
        CheckConstraint(
            'shareability BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_shareability',
        ),
        CheckConstraint(
            'memorability BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_memorability',
        ),
        CheckConstraint(
            'quotation_potential BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_quotation_potential',
        ),
        CheckConstraint(
            'discussion_potential BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_discussion_potential',
        ),
    )
