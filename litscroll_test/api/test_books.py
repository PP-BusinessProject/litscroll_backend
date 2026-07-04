import pytest

from litscroll_api.repositories.book_repository import BookRepository
from litscroll_db.models.public.book import Book
from litscroll_db.models.public.book_genre import BookGenre
from litscroll_db.models.public.book_quote import BookQuote
from litscroll_db.models.public.genre import Genre


## Fixtures


@pytest.fixture
async def repository(db):
    return BookRepository(db)


## Фикстура с тестовыми данными


@pytest.fixture
async def seed(db):
    fantasy = Genre(name='Fantasy')
    dystopia = Genre(name='Dystopia')

    db.add_all([fantasy, dystopia])
    await db.flush()

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

    db.add_all([hobbit, nineteen, hp])
    await db.flush()

    db.add_all(
        [
            BookGenre(book_id=hobbit.id, genre_id=fantasy.id),
            BookGenre(book_id=hp.id, genre_id=fantasy.id),
            BookGenre(book_id=nineteen.id, genre_id=dystopia.id),
        ]
    )

    db.add_all(
        [
            BookQuote(
                book_id=hobbit.id,
                like_count=10,
                paragraphs=['One'],
            ),
            BookQuote(
                book_id=hp.id,
                like_count=30,
                paragraphs=['Two'],
            ),
            BookQuote(
                book_id=nineteen.id,
                like_count=20,
                paragraphs=['Three'],
            ),
        ]
    )

    return {
        'fantasy': fantasy,
        'dystopia': dystopia,
        'hobbit': hobbit,
        'nineteen': nineteen,
        'hp': hp,
    }


## GET /books


@pytest.mark.asyncio
async def test_get_books(client, seed):
    response = await client.get('/books')

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 3

    assert body[0]['title'] == 'The Hobbit'
    assert body[1]['title'] == '1984'
    assert body[2]['title'] == 'Harry Potter'


## GET /books/{id}


@pytest.mark.asyncio
async def test_get_book(client, seed):
    response = await client.get(f'/books/{seed["hobbit"].id}')

    assert response.status_code == 200

    body = response.json()

    assert body['title'] == 'The Hobbit'
    assert body['author_name'] == 'Tolkien'


## GET /books/popular


@pytest.mark.asyncio
async def test_get_popular_books(client, seed):
    response = await client.get('/books/popular')

    assert response.status_code == 200

    body = response.json()

    assert body[0]['title'] == 'Harry Potter'
    assert body[1]['title'] == '1984'
    assert body[2]['title'] == 'The Hobbit'


## GET /books/genre/{id}


@pytest.mark.asyncio
async def test_get_books_by_genre(client, seed):
    response = await client.get(f'/books/genre/{seed["fantasy"].id}')

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2

    titles = {book['title'] for book in body}

    assert titles == {
        'The Hobbit',
        'Harry Potter',
    }
