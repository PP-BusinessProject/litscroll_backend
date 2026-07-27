from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, SmallInteger
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql.schema import Column

from ..base import Base
from .book_quote import BookQuote

if TYPE_CHECKING:
    from .book_quote import BookQuote


class ExcerptRanking(Base):
    __tablename__ = 'excerpt_ranking'

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

    overall_score: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'overall_score BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_overall_score',
        ),
        nullable=False,
    )

    hook_strength: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'hook_strength BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_hook_strength',
        ),
        nullable=False,
    )

    continue_reading_pressure: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'continue_reading_pressure BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_continue_reading_pressure',
        ),
        nullable=False,
    )

    curiosity: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'curiosity BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_curiosity',
        ),
        nullable=False,
    )

    suspense: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'suspense BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_suspense',
        ),
        nullable=False,
    )

    emotional_intensity: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'emotional_intensity BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_emotional_intensity',
        ),
        nullable=False,
    )

    beauty_of_writing: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'beauty_of_writing BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_beauty_of_writing',
        ),
        nullable=False,
    )

    thought_provoking: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'thought_provoking BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_thought_provoking',
        ),
        nullable=False,
    )

    viral_potential: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'viral_potential BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_viral_potential',
        ),
        nullable=False,
    )

    shareability: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'shareability BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_shareability',
        ),
        nullable=False,
    )

    memorability: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'memorability BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_memorability',
        ),
        nullable=False,
    )

    quotation_potential: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'quotation_potential BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_quotation_potential',
        ),
        nullable=False,
    )

    discussion_potential: Mapped[int] = Column(
        SmallInteger,
        CheckConstraint(
            'discussion_potential BETWEEN 0 AND 100',
            name='ck_excerpt_ranking_discussion_potential',
        ),
        nullable=False,
    )

    quote: Mapped['BookQuote'] = relationship(
        back_populates='ranking',
    )
