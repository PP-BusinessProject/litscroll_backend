from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.types import VARCHAR

from ..base import Base
from .book_quote import BookQuote

if TYPE_CHECKING:
    from .book_quote import BookQuote


class ExcerptNarrative(Base):
    __tablename__ = 'excerpt_narrative'

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

    scene_type: Mapped[str] = Column(
        VARCHAR(100),
        nullable=False,
    )

    story_role: Mapped[str] = Column(
        VARCHAR(100),
        nullable=False,
    )

    contains_cliffhanger: Mapped[bool] = Column(
        Boolean,
        nullable=False,
    )

    contains_reveal: Mapped[bool] = Column(
        Boolean,
        nullable=False,
    )

    contains_twist: Mapped[bool] = Column(
        Boolean,
        nullable=False,
    )

    contains_major_decision: Mapped[bool] = Column(
        Boolean,
        nullable=False,
    )

    contains_character_growth: Mapped[bool] = Column(
        Boolean,
        nullable=False,
    )

    contains_worldbuilding: Mapped[bool] = Column(
        Boolean,
        nullable=False,
    )

    spoiler_level: Mapped[int] = Column(
        Integer,
        CheckConstraint(
            'spoiler_level BETWEEN 0 AND 4',
            name='ck_excerpt_narrative_spoiler_level',
        ),
        nullable=False,
    )

    quote: Mapped['BookQuote'] = relationship(
        back_populates='narrative',
    )
