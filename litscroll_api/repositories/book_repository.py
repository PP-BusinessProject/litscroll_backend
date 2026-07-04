from typing import Self

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import func

from litscroll_db.models.public.book import Book
from litscroll_db.models.public.book_genre import BookGenre
from litscroll_db.models.public.book_quote import BookQuote


class BookRepository:
    def __init__(self: Self, session: AsyncSession):
        self.session = session

    async def get_by_id(self: Self, book_id: int) -> Book | None:
        return await self.session.get(Book, book_id)

    async def get_all(self: Self, offset: int, limit: int) -> list[Book]:
        result = await self.session.execute(
            select(Book).offset(offset).limit(limit)
        )

        return result.scalars().all()

    async def get_by_genre(
        self: Self,
        genre_id: int,
        offset: int,
        limit: int,
    ) -> list[Book]:
        result = await self.session.execute(
            select(Book)
            .join(BookGenre, BookGenre.book_id == Book.id)
            .where(BookGenre.genre_id == genre_id)
            .order_by(Book.id)
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_popular(self: Self, offset: int, limit: int) -> list[Book]:
        result = await self.session.execute(
            select(Book)
            .join(BookQuote, BookQuote.book_id == Book.id)
            .group_by(Book.id)
            .order_by(desc(func.sum(BookQuote.like_count)))
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_with_quotes(self: Self, book_id: int) -> Book | None:
        result = await self.session.execute(
            select(Book)
            .where(Book.id == book_id)
            .options(selectinload(Book.quotes))
        )

        return result.scalar_one_or_none()
