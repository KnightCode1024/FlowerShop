from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        print(self.session)
        return self

    async def __aexit__(self, exception_type, exception, traceback):
        print(exception_type, exception, traceback)

        if exception_type:
            await self.session.rollback()
            print("Session rollback")
        else:
            await self.session.commit()
            print("Session committed")

        await self.session.close()
        print("Session closed")
