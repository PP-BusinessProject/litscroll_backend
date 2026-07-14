from uuid import uuid4

import pytest

from litscroll_api.repositories.user_repository import UserRepository
from litscroll_db.models.auth.user import User
from litscroll_db.models.public.book import Book
from litscroll_db.models.public.book_quote import BookQuote
from litscroll_db.models.public.book_quote_user import BookQuoteUser


# Fixtures


@pytest.fixture
async def repository(db):
    return UserRepository(db)


@pytest.fixture
async def seed(db):
    user = User(id=uuid4())

    book = Book(
        title='The Hobbit',
        description='Fantasy',
        author_name='Tolkien',
        year=1937,
        page_count=310,
    )

    db.add_all([user, book])
    await db.flush()

    quote1 = BookQuote(
        book_id=book.id,
        like_count=10,
        paragraphs=['One'],
    )

    quote2 = BookQuote(
        book_id=book.id,
        like_count=20,
        paragraphs=['Two'],
    )

    db.add_all([quote1, quote2])
    await db.flush()

    relation1 = BookQuoteUser(
        user_id=user.id,
        quote_id=quote1.id,
        progress=40,
        liked_at=None,
        finished_at=None,
    )

    relation2 = BookQuoteUser(
        user_id=user.id,
        quote_id=quote2.id,
        progress=100,
        liked_at=None,
        finished_at=None,
    )

    db.add_all([relation1, relation2])
    await db.commit()

    return {
        'user': user,
        'quote1': quote1,
        'quote2': quote2,
    }


# GET /users/{id}


@pytest.mark.asyncio
async def test_get_user(client, seed):
    response = await client.get(f'/users/{seed["user"].id}')

    assert response.status_code == 200

    body = response.json()

    assert body['id'] == str(seed['user'].id)


# GET /users/{id}/quotes


@pytest.mark.asyncio
async def test_get_user_quotes(client, seed):
    response = await client.get(f'/users/{seed["user"].id}/quotes')

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2


# GET /users/{id}/quotes/{quote_id}/progress


@pytest.mark.asyncio
async def test_get_progress(client, seed):
    response = await client.get(
        f'/users/{seed["user"].id}/quotes/{seed["quote1"].id}/progress'
    )

    assert response.status_code == 200

    assert response.json() == 40


# PATCH /users/{id}/quotes/{quote_id}/progress


@pytest.mark.asyncio
async def test_update_progress(client, seed):
    response = await client.patch(
        f'/users/{seed["user"].id}/quotes/{seed["quote1"].id}/progress?progress=80'
    )

    assert response.status_code == 200

    response = await client.get(
        f'/users/{seed["user"].id}/quotes/{seed["quote1"].id}/progress'
    )

    assert response.json() == 80


# PATCH /users/{id}/quotes/{quote_id}/finish


@pytest.mark.asyncio
async def test_mark_finished(client, seed):
    response = await client.patch(
        f'/users/{seed["user"].id}/quotes/{seed["quote1"].id}/finish'
    )

    assert response.status_code == 200


# PATCH /users/{id}/quotes/{quote_id}/like


@pytest.mark.asyncio
async def test_like_quote(client, seed):
    response = await client.patch(
        f'/users/{seed["user"].id}/quotes/{seed["quote1"].id}/like'
    )

    assert response.status_code == 200


# GET /users/{id}/favorites


@pytest.mark.asyncio
async def test_get_favorites(client, seed):
    await client.patch(
        f'/users/{seed["user"].id}/quotes/{seed["quote1"].id}/like'
    )

    response = await client.get(f'/users/{seed["user"].id}/favorites')

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1

    assert body[0]['id'] == seed['quote1'].id
