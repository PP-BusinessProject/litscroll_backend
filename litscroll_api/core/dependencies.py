# dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.book_repository import BookRepository
from .database import get_db


def get_book_repository(
    session: AsyncSession = Depends(get_db),
) -> BookRepository:
    return BookRepository(session)
