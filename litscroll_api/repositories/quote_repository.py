from uuid import UUID

from sqlalchemy import desc, select

from litscroll_db.models.public.book_quote import BookQuote
from litscroll_db.models.public.book_quote_user import BookQuoteUser


class QuoteRepository:
    def __init__(self, session):
        self.session = session

    async def get_by_id(self, quote_id: int) -> BookQuote | None:
        return await self.session.get(BookQuote, quote_id)

    async def get_by_book(self, book_id: int) -> list[BookQuote]:
        result = await self.session.execute(
            select(BookQuote).where(BookQuote.book_id == book_id)
        )

        return result.scalars().all()

    async def get_suggested_for_user(
        self,
        user_id: UUID,
        limit: int = 10,
    ) -> list[BookQuote]:
        subquery = select(BookQuoteUser.quote_id).where(
            BookQuoteUser.user_id == user_id
        )

        result = await self.session.execute(
            select(BookQuote)
            .where(BookQuote.id.not_in(subquery))
            .order_by(desc(BookQuote.like_count))
            .limit(limit)
        )

        return result.scalars().all()

    async def get_popular(self, limit: int) -> list[BookQuote]:
        result = await self.session.execute(
            select(BookQuote).order_by(desc(BookQuote.like_count)).limit(limit)
        )

        return result.scalars().all()
