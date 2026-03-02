from typing import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncSession

from core.uow import UnitOfWork
from dishka import provide, Scope, Provider

from entrypoint.ioc.engine import session_factory


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def session(self) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def uow(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session)