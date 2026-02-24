from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from entrypoint.config import config
from dishka import Provider, Scope, provide


class DatabaseProvider(Provider):
    scope = Scope.REQUEST

    engine = create_async_engine(
        config.database.DATABASE_URI,
        future=True,
    )
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        autoflush=False,
    )

    @provide
    async def get_db_session(self) -> AsyncGenerator[AsyncSession]:
        async with self.session_factory() as session:
            yield session
