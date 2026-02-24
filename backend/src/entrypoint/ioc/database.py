from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from entrypoint.config import config
<<<<<<< HEAD
=======
from entrypoint.ioc.engine import session_factory
>>>>>>> origin/main


class DatabaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_db_session(self) -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session:
            yield session
