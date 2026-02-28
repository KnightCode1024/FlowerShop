from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from dishka import Provider, Scope, provide
from entrypoint.ioc.engine import session_factory


class DatabaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session
