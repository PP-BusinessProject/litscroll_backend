from threading import Thread

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from litscroll_api.__main__ import app
from litscroll_api.core.config import get_settings
from litscroll_api.core.database import get_db
from litscroll_db.__main__ import cli as clear_db


clear_thread = Thread(None, clear_db)
clear_thread.start()
clear_thread.join()


@pytest_asyncio.fixture
async def db():
    settings = get_settings()
    engine = create_async_engine(
        'postgresql+asyncpg://'
        + settings.database_url.split('://')[-1].split('?')[0].strip(),
        future=True,
    )

    TestingSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db):

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test',
    ) as client:
        yield client

    app.dependency_overrides.clear()
