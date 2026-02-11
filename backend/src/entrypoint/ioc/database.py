from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from entrypoint.config import create_config


class DatabaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_db_session(self) -> AsyncGenerator[AsyncSession]:
        async with self._get_session_factory() as session:
            yield session

    def _get_session_factory(self):
        config = create_config()
        engine = create_async_engine(
            url=config.database.get_db_url(),
        )
        session_factory = async_sessionmaker(
            engine,
            expire_on_commit=False,
        )
        return session_factory
