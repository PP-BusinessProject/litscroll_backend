from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

from ..base import Base
from .book import Book


if TYPE_CHECKING:
    from .book import Book
    from .excerpt_engagement_prediction import (
        ExcerptEngagementPrediction,
    )
    from .excerpt_narrative import ExcerptNarrative
    from .excerpt_ranking import ExcerptRanking
    from .excerpt_style_analysis import ExcerptStyleAnalysis


class BookExcerptAnalysis(Base):
    __tablename__ = 'book_excerpt_analysis'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    book_id: Mapped[int] = mapped_column(
        ForeignKey(
            Book.id,
            ondelete='CASCADE',
        ),
        nullable=False,
        index=True,
    )

    embedding_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # [
    #     ["Параграф 1 страницы 1", "Параграф 2 страницы 1"],
    #     ["Параграф 1 страницы 2"]
    # ]
    excerpt_text: Mapped[list[list[str]]] = mapped_column(
        JSONB,
        nullable=False,
    )

    word_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    opening_hook: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    best_quote: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    one_sentence_pitch: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    themes: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )

    keywords: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )

    observations: Mapped[dict[str, list[Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    book: Mapped['Book'] = relationship(
        back_populates='excerpt_analyses',
    )

    ranking: Mapped['ExcerptRanking'] = relationship(
        back_populates='analysis',
        uselist=False,
        cascade='all, delete-orphan',
    )

    narrative: Mapped['ExcerptNarrative'] = relationship(
        back_populates='analysis',
        uselist=False,
        cascade='all, delete-orphan',
    )

    style_analysis: Mapped['ExcerptStyleAnalysis'] = relationship(
        back_populates='analysis',
        uselist=False,
        cascade='all, delete-orphan',
    )

    engagement_prediction: Mapped['ExcerptEngagementPrediction'] = (
        relationship(
            back_populates='analysis',
            uselist=False,
            cascade='all, delete-orphan',
        )
    )

    __table_args__ = (
        CheckConstraint(
            'word_count >= 0',
            name='ck_book_excerpt_analysis_word_count',
        ),
    )
