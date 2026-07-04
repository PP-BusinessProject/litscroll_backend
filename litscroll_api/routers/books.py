from fastapi import APIRouter, Depends, HTTPException

from ..core.dependencies import get_book_repository
from ..repositories.book_repository import BookRepository


router = APIRouter(prefix='/books', tags=['Books'])


@router.get('/{book_id}')
async def get_book(
    book_id: int,
    repo: BookRepository = Depends(get_book_repository),
):
    book = await repo.get_by_id(book_id)

    if book is None:
        raise HTTPException(404)

    return book


@router.get('')
async def get_books(
    page: int = 1,
    limit: int = 20,
    repo: BookRepository = Depends(get_book_repository),
):
    return await repo.get_all(page, limit)


@router.get('/popular')
async def popular_books(
    repo: BookRepository = Depends(get_book_repository),
):
    return await repo.get_popular(20)


@router.get('/genre/{genre_id}')
async def by_genre(
    genre_id: int,
    repo: BookRepository = Depends(get_book_repository),
):
    return await repo.get_by_genre(genre_id)
