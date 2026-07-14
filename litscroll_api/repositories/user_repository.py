from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update

from litscroll_db.models.auth.user import User
from litscroll_db.models.public.book_quote import BookQuote
from litscroll_db.models.public.book_quote_user import BookQuoteUser


class UserRepository:
    def __init__(self, session):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_user_quotes(
        self,
        user_id: UUID,
        offset: int,
        limit: int,
    ) -> list[BookQuote]:
        result = await self.session.execute(
            select(BookQuote)
            .join(BookQuoteUser, BookQuoteUser.quote_id == BookQuote.id)
            .where(BookQuoteUser.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_quote_progress(
        self,
        user_id: UUID,
        quote_id: int,
    ) -> int | None:
        result = await self.session.execute(
            select(BookQuoteUser.progress).where(
                BookQuoteUser.user_id == user_id,
                BookQuoteUser.quote_id == quote_id,
            )
        )

        return result.scalar_one_or_none()

    async def update_progress(
        self,
        user_id: UUID,
        quote_id: int,
        progress: int,
    ) -> None:
        await self.session.execute(
            update(BookQuoteUser)
            .where(
                BookQuoteUser.user_id == user_id,
                BookQuoteUser.quote_id == quote_id,
            )
            .values(progress=progress)
        )

        await self.session.commit()

    async def mark_finished(self, user_id: UUID, quote_id: int) -> None:
        await self.session.execute(
            update(BookQuoteUser)
            .where(
                BookQuoteUser.user_id == user_id,
                BookQuoteUser.quote_id == quote_id,
            )
            .values(finished_at=datetime.now())
        )
        await self.session.commit()

    async def like_quote(self, user_id: UUID, quote_id: int) -> None:
        await self.session.execute(
            update(BookQuoteUser)
            .where(
                BookQuoteUser.user_id == user_id,
                BookQuoteUser.quote_id == quote_id,
                BookQuoteUser.liked_at.is_(None),
            )
            .values(liked_at=datetime.now())
        )

        await self.session.execute(
            update(BookQuote)
            .where(BookQuote.id == quote_id)
            .values(like_count=BookQuote.like_count + 1)
        )

        await self.session.commit()

    async def unlike_quote(self, user_id: UUID, quote_id: int) -> None:
        await self.session.execute(
            update(BookQuoteUser)
            .where(
                BookQuoteUser.user_id == user_id,
                BookQuoteUser.quote_id == quote_id,
                BookQuoteUser.liked_at.is_not(None),
            )
            .values(liked_at=None)
        )

        await self.session.execute(
            update(BookQuote)
            .where(BookQuote.id == quote_id)
            .values(like_count=BookQuote.like_count - 1)
        )

        await self.session.commit()

    async def get_favorites(
        self,
        user_id: UUID,
        offset: int,
        limit: int,
    ) -> list[BookQuote]:
        result = await self.session.execute(
            select(BookQuote)
            .join(BookQuoteUser, BookQuoteUser.quote_id == BookQuote.id)
            .where(
                BookQuoteUser.user_id == user_id,
                BookQuoteUser.liked_at.is_not(None),
            )
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()
