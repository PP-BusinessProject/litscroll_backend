from fastapi import APIRouter, Depends, HTTPException

from ..core.dependencies import get_book_repository
from ..repositories.book_repository import BookRepository


router = APIRouter(prefix='/books', tags=['Books'])


@router.get('/popular')
async def popular_books(
    offset: int = 0,
    limit: int = 20,
    repo: BookRepository = Depends(get_book_repository),
):
    return await repo.get_popular(offset, limit)


@router.get('/genre/{genre_id}')
async def by_genre(
    genre_id: int,
    offset: int = 0,
    limit: int = 20,
    repo: BookRepository = Depends(get_book_repository),
):
    return await repo.get_by_genre(genre_id, offset, limit)


@router.get('')
async def get_books(
    offset: int = 0,
    limit: int = 20,
    repo: BookRepository = Depends(get_book_repository),
):
    return await repo.get_all(offset, limit)


@router.get('/{book_id}')
async def get_book(
    book_id: int,
    repo: BookRepository = Depends(get_book_repository),
):
    book = await repo.get_by_id(book_id)

    if book is None:
        raise HTTPException(404)

    return book
