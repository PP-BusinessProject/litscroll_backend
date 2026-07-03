from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload

from litscroll_db.models.public.book import Book
from litscroll_db.models.public.book_genre import BookGenre
from litscroll_db.models.public.book_quote import BookQuote


class BookRepository:
    def __init__(self, session):
        self.session = session

    async def get_by_id(self, book_id: int) -> Book | None:
        return await self.session.get(Book, book_id)

    async def get_all(self, page: int, limit: int) -> list[Book]:
        offset = (page - 1) * limit

        result = await self.session.execute(
            select(Book).offset(offset).limit(limit)
        )

        return result.scalars().all()

    # async def search(self, query):

    async def get_by_genre(self, genre_id: int) -> list[Book]:
        result = await self.session.execute(
            select(Book)
            .join(BookGenre, BookGenre.book_id == Book.id)
            .where(BookGenre.genre_id == genre_id)
            .order_by(Book.id)
        )

        return result.scalars().all()

    async def get_popular(self, limit: int) -> list[Book]:
        result = await self.session.execute(
            select(Book)
            .join(BookQuote, BookQuote.book_id == Book.id)
            .order_by(desc(BookQuote.like_count))
            .limit(limit)
        )

        return result.scalars().all()

    async def get_with_quotes(self, book_id: int) -> Book | None:
        result = await self.session.execute(
            select(Book)
            .options(selectinload(Book.quotes))
            .where(Book.id == book_id)
        )

        return result.scalar_one_or_none()
