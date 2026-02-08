from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from dishka import (
    Provider,
    provide,
    Scope,
    AsyncContainer,
    make_async_container,
)

from src.models import (
    Base,
    # User,
    # Category,
    # Product,
    # ProductImage,
    # RoleEnum,
)
from src.entrypoint.config import Config


@pytest.fixture(scope="session")
def postgres_url():
    return "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def sync_engine():
    # from src.models import Base

    # from sqlalchemy import create_engine

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    return engine


@pytest.fixture(scope="session")
async def async_engine(postgres_url):
    engine = create_async_engine(
        postgres_url,
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    return engine


@pytest.fixture(scope="session")
async def async_session_maker(
    async_engine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=async_engine,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest.fixture
def database_provider(session: AsyncSession):
    class TestDatabaseProvider(Provider):
        @provide(scope=Scope.REQUEST)
        async def get_session(self):
            return session

    return TestDatabaseProvider()


@pytest.fixture
def container(database_provider: Provider) -> AsyncContainer:
    return make_async_container(
        database_provider,
        context={Config: MagicMock},
    )
