from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from dishka import Provider, Scope, provide

from entrypoint.config import config
from entrypoint.ioc.engine import session_factory


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def engine(self) -> AsyncEngine:
        return create_async_engine(config.database.DATABASE_URI)

    @provide(scope=Scope.REQUEST)
    async def session(self, engine: AsyncEngine) -> AsyncIterable[AsyncSession]:
        async with AsyncSession(engine) as session:
            yield session