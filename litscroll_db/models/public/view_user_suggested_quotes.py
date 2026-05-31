from typing import ClassVar, Self, Type

from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql import case, func, select
from sqlalchemy.sql.selectable import Select

from ...utils.descriptors import cachedclassproperty
from ..base import Base, BaseInterface, TableArgs
from .book_genre import BookGenre
from .book_quote import BookQuote
from .book_quote_user import BookQuoteUser


class ViewUserSuggestedQuotes(BaseInterface):
    user_id: Mapped[int]
    quote_id: Mapped[int]
    score: Mapped[float]

    @cachedclassproperty
    def __selectable__(cls: Type[Self], /) -> Select:
        """
        View: personalized quote recommendations
        based on genre affinity + popularity + recency
        """

        # -----------------------------
        # 1. USER GENRE AFFINITY MODEL
        # -----------------------------
        genre_scores = (
            select(
                BookQuoteUser.user_id.label('user_id'),
                BookGenre.genre_id.label('genre_id'),
                func.sum(
                    case(
                        # strong signal: finished and liked quote
                        (
                            BookQuoteUser.finished_at.is_not(None)
                            & BookQuoteUser.liked_at.is_not(None),
                            8,
                        ),
                        # strong signal: finished quote
                        (BookQuoteUser.finished_at.is_not(None), 5),
                        # medium signal: liked quote
                        (BookQuoteUser.liked_at.is_not(None), 2),
                        # weak signal: partial progress
                        else_=func.coalesce(BookQuoteUser.progress, 0) / 100.0,
                    )
                ).label('affinity_score'),
            )
            .select_from(BookQuoteUser)
            .join(
                BookQuote,
                BookQuote.id == BookQuoteUser.quote_id,
            )
            .join(
                BookGenre,
                BookGenre.book_id == BookQuote.book_id,
            )
            .group_by(
                BookQuoteUser.user_id,
                BookGenre.genre_id,
            )
            .subquery()
        )

        # -----------------------------
        # 2. ALREADY SEEN QUOTES
        # -----------------------------
        seen_quotes = select(
            BookQuoteUser.user_id,
            BookQuoteUser.quote_id,
        ).subquery()

        # -----------------------------
        # 3. AGE IN DAYS (recency decay)
        # -----------------------------
        age_days = (
            func.extract(
                'epoch',
                func.now() - BookQuote.created_at,
            )
            / 86400
        )

        # -----------------------------
        # 4. FINAL RECOMMENDATION QUERY
        # -----------------------------
        return (
            select(
                genre_scores.c.user_id,
                BookQuote.id.label('quote_id'),
                (
                    # genre preference dominates
                    genre_scores.c.affinity_score * 100
                    # popularity signal
                    + func.ln(func.coalesce(BookQuote.like_count, 0) + 1) * 25
                    # freshness penalty
                    - age_days * 0.5
                ).label('score'),
            )
            .select_from(genre_scores)
            .join(
                BookGenre,
                BookGenre.genre_id == genre_scores.c.genre_id,
            )
            .join(
                BookQuote,
                BookQuote.book_id == BookGenre.book_id,
            )
            .outerjoin(
                seen_quotes,
                (seen_quotes.c.user_id == genre_scores.c.user_id)
                & (seen_quotes.c.quote_id == BookQuote.id),
            )
            .where(
                seen_quotes.c.quote_id.is_(None),
            )
        )

    __table_args__: ClassVar[TableArgs] = (
        dict(
            schema='public',
            comment='View with personalized quote recommendations',
        ),
    )


Base.registry.map_imperatively(
    ViewUserSuggestedQuotes,
    ViewUserSuggestedQuotes.__table__,
)
