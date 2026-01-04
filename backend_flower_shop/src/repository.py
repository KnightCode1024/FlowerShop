from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Post


class PostRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.model = Post
        self.session = session

    async def get_post_by_id(self, id: int):
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all_posts(self, offset: int = 0, limit: int = 20, **kwargs):
        query = select(self.model).offset(offset).limit(limit)

        if "options" in kwargs:
            query = query.options[*kwargs["options"]]

        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_post(self, data: dict):
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update_post(self, id: int, data: dict):
        instance = await self.get_post_by_id(id)
        if not instance:
            return None

        for key, value in data.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete_post(self, id: int):
        instance = await self.get_by_id(id)
        if instance:
            await self.session.delete(instance)
            await self.session.commit()
            return True
        return False
