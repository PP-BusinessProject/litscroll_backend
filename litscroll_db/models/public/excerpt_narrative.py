from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .book_excerpt_analysis import BookExcerptAnalysis


if TYPE_CHECKING:
    from .book_excerpt_analysis import BookExcerptAnalysis


class ExcerptNarrative(Base):
    __tablename__ = 'excerpt_narrative'

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

    scene_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    story_role: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    contains_cliffhanger: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    contains_reveal: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    contains_twist: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    contains_major_decision: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    contains_character_growth: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    contains_worldbuilding: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    spoiler_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    analysis: Mapped['BookExcerptAnalysis'] = relationship(
        back_populates='narrative',
    )

    __table_args__ = (
        CheckConstraint(
            'spoiler_level BETWEEN 0 AND 4',
            name='ck_excerpt_narrative_spoiler_level',
        ),
    )
