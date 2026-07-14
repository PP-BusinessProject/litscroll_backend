# dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.quote_repository import QuoteRepository
from ..repositories.user_repository import UserRepository
from ..repositories.book_repository import BookRepository
from .database import get_db


def get_book_repository(
    session: AsyncSession = Depends(get_db),
) -> BookRepository:
    return BookRepository(session)


def get_quote_repository(
    session: AsyncSession = Depends(get_db),
) -> QuoteRepository:
    return QuoteRepository(session)


def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    return UserRepository(session)
