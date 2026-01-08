from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class BaseRepository:
    def __init__(
        self,
        model,
        session: AsyncSession,
    ):
        self.model = model
        self.session = session

    async def create(
        self,
        data: dict,
    ):
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get(
        self,
        id: int,
    ):
        result = await self.session.execute(
            select(self.model).where(self.model.id == id),
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ):
        result = await self.session.execute(
            select(self.model).offset(offset).limit(limit),
        )
        return result.scalars().all()

    async def update(
        self,
        id: int,
        data: dict,
    ):
        instance = self.get(id)
        if not instance:
            return None

        for key, value in data:
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(
        self,
        id: int,
    ) -> bool:
        instance = self.get(id)
        if instance:
            await self.session.delete(instance)
            await self.session.commit()
            return True
        return False
