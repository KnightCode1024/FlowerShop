from typing import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from src.flowershop_api.entrypoint.config import config

engine = create_async_engine(
    url=config.database.get_db_url(),
)
session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


class DatabaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session
