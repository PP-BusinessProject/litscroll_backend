from uuid import uuid4

import pytest

from litscroll_api.repositories.quote_repository import QuoteRepository
from litscroll_db.models.auth.user import User
from litscroll_db.models.public.book import Book
from litscroll_db.models.public.book_quote import BookQuote
from litscroll_db.models.public.book_quote_user import BookQuoteUser


# Fixtures


@pytest.fixture
async def repository(db):
    return QuoteRepository(db)


@pytest.fixture
async def seed(db):
    user = User(id=uuid4())

    hobbit = Book(
        title='The Hobbit',
        description='Fantasy',
        author_name='Tolkien',
        year=1937,
        page_count=310,
    )

    nineteen = Book(
        title='1984',
        description='Dystopia',
        author_name='George Orwell',
        year=1949,
        page_count=328,
    )

    hp = Book(
        title='Harry Potter',
        description='Wizard',
        author_name='Rowling',
        year=1997,
        page_count=400,
    )

    db.add(user)
    db.add_all([hobbit, nineteen, hp])
    await db.flush()

    hobbit_quote = BookQuote(
        book_id=hobbit.id,
        like_count=10,
        paragraphs=['One'],
    )

    nineteen_quote = BookQuote(
        book_id=nineteen.id,
        like_count=20,
        paragraphs=['Three'],
    )

    hp_quote = BookQuote(
        book_id=hp.id,
        like_count=30,
        paragraphs=['Two'],
    )

    second_hp_quote = BookQuote(
        book_id=hp.id,
        like_count=15,
        paragraphs=['Four'],
    )

    db.add_all(
        [
            hobbit_quote,
            nineteen_quote,
            hp_quote,
            second_hp_quote,
        ]
    )
    await db.flush()

    db.add(
        BookQuoteUser(
            user_id=user.id,
            quote_id=hobbit_quote.id,
            progress=50,
        )
    )
    await db.flush()

    return {
        'user': user,
        'hobbit': hobbit,
        'nineteen': nineteen,
        'hp': hp,
        'hobbit_quote': hobbit_quote,
        'nineteen_quote': nineteen_quote,
        'hp_quote': hp_quote,
        'second_hp_quote': second_hp_quote,
    }


# GET /quotes/{quote_id}


@pytest.mark.asyncio
async def test_get_quote(client, seed):
    response = await client.get(f'/quotes/{seed["hobbit_quote"].id}')

    assert response.status_code == 200

    body = response.json()

    assert body['id'] == seed['hobbit_quote'].id
    assert body['book_id'] == seed['hobbit'].id
    assert body['like_count'] == 10
    assert body['paragraphs'] == ['One']


@pytest.mark.asyncio
async def test_get_quote_not_found(client, seed):
    response = await client.get('/quotes/999999')

    assert response.status_code == 404


# GET /quotes/book/{book_id}


@pytest.mark.asyncio
async def test_get_quotes_by_book(client, seed):
    response = await client.get(
        f'/quotes/book/{seed["hp"].id}?offset=0&limit=10'
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2

    paragraphs = {tuple(quote['paragraphs']) for quote in body}

    assert paragraphs == {
        ('Two',),
        ('Four',),
    }


@pytest.mark.asyncio
async def test_get_quotes_by_book_pagination(client, seed):
    response = await client.get(
        f'/quotes/book/{seed["hp"].id}?offset=1&limit=1'
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]['book_id'] == seed['hp'].id


# GET /quotes/popular


@pytest.mark.asyncio
async def test_get_popular_quotes(client, seed):
    response = await client.get('/quotes/popular?offset=0&limit=10')

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 4

    assert body[0]['like_count'] == 30
    assert body[1]['like_count'] == 20
    assert body[2]['like_count'] == 15
    assert body[3]['like_count'] == 10


@pytest.mark.asyncio
async def test_get_popular_quotes_pagination(client, seed):
    response = await client.get('/quotes/popular?offset=1&limit=2')

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]['like_count'] == 20
    assert body[1]['like_count'] == 15


# GET /quotes/user/{user_id}


@pytest.mark.asyncio
async def test_get_suggested_quotes_for_user(client, seed):
    response = await client.get(
        f'/quotes/suggested/{seed["user"].id}?offset=0&limit=10'
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 3

    returned_ids = {quote['id'] for quote in body}

    # Эта цитата уже связана с пользователем
    assert seed['hobbit_quote'].id not in returned_ids

    assert seed['hp_quote'].id in returned_ids
    assert seed['nineteen_quote'].id in returned_ids
    assert seed['second_hp_quote'].id in returned_ids


@pytest.mark.asyncio
async def test_get_suggested_quotes_pagination(client, seed):
    response = await client.get(
        f'/quotes/suggested/{seed["user"].id}?offset=1&limit=1'
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1

    # Доступные цитаты сортируются так:
    # 30, 20, 15. После offset=1 вернётся цитата с 20 лайками.
    assert body[0]['id'] == seed['nineteen_quote'].id
    assert body[0]['like_count'] == 20
