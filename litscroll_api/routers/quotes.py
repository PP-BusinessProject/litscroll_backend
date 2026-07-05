from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ..core.dependencies import get_quote_repository
from ..repositories.quote_repository import QuoteRepository


router = APIRouter(prefix='/quotes', tags=['Quotes'])


@router.get('/popular')
async def popular_books(
    limit: int = 20,
    repo: QuoteRepository = Depends(get_quote_repository),
):
    return await repo.get_popular(limit)


@router.get('/book/{book_id}')
async def by_book(
    book_id: int,
    repo: QuoteRepository = Depends(get_quote_repository),
):
    return await repo.get_by_book(book_id)


@router.get('/suggested/{user_id}')
async def suggested_for_user(
    user_id: UUID,
    limit: int = 10,
    repo: QuoteRepository = Depends(get_quote_repository),
):
    return await repo.get_suggested_for_user(user_id, limit)


@router.get('/{quote_id}')
async def get_quote(
    quote_id: int,
    repo: QuoteRepository = Depends(get_quote_repository),
):
    quote = await repo.get_by_id(quote_id)

    if quote is None:
        raise HTTPException(404)

    return quote
