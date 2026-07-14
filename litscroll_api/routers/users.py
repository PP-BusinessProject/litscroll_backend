from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ..core.dependencies import get_user_repository
from ..repositories.user_repository import UserRepository


router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/{user_id}')
async def get_user(
    user_id: UUID,
    repo: UserRepository = Depends(get_user_repository),
):
    user = await repo.get_by_id(user_id)

    if user is None:
        raise HTTPException(404)

    return user


@router.get('/{user_id}/quotes')
async def user_quotes(
    user_id: UUID,
    offset: int = 0,
    limit: int = 20,
    repo: UserRepository = Depends(get_user_repository),
):
    return await repo.get_user_quotes(user_id, offset, limit)


@router.get('/{user_id}/quotes/{quote_id}/progress')
async def get_quote_progress(
    user_id: UUID,
    quote_id: int,
    repo: UserRepository = Depends(get_user_repository),
):
    return await repo.get_quote_progress(user_id, quote_id)


@router.patch('/{user_id}/quotes/{quote_id}/progress')
async def update_progress(
    user_id: UUID,
    quote_id: int,
    progress: int,
    repo: UserRepository = Depends(get_user_repository),
):
    await repo.update_progress(user_id, quote_id, progress)
    return {'message': 'Progress updated'}


@router.patch('/{user_id}/quotes/{quote_id}/finish')
async def mark_finished(
    user_id: UUID,
    quote_id: int,
    repo: UserRepository = Depends(get_user_repository),
):
    await repo.mark_finished(user_id, quote_id)
    return {'message': 'Quote marked as finished'}


@router.patch('/{user_id}/quotes/{quote_id}/like')
async def like_quote(
    user_id: UUID,
    quote_id: int,
    repo: UserRepository = Depends(get_user_repository),
):
    await repo.like_quote(user_id, quote_id)
    return {'message': 'Quote liked'}


@router.patch('/{user_id}/quotes/{quote_id}/unlike')
async def unlike_quote(
    user_id: UUID,
    quote_id: int,
    repo: UserRepository = Depends(get_user_repository),
):
    await repo.unlike_quote(user_id, quote_id)
    return {'message': 'Quote unliked'}


@router.get('/{user_id}/favorites')
async def get_favorites(
    user_id: UUID,
    offset: int = 0,
    limit: int = 20,
    repo: UserRepository = Depends(get_user_repository),
):
    return await repo.get_favorites(user_id, offset, limit)
