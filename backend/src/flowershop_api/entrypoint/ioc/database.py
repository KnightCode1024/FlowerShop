from typing import AsyncGenerator

from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from flowershop_api.entrypoint.config import create_config


class DatabaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        config = create_config()
        engine = create_async_engine(
            url=config.database.get_db_url(),
        )
        session_factory = async_sessionmaker(
            engine,
            expire_on_commit=False,
        )
        async with session_factory() as session:
            yield session
