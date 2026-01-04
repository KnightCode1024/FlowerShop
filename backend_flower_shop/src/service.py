from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from models import Post
from repository import PostRepository


class PostService:
    def __init__(self, session: AsyncSession):
        self.post_repo = PostRepository(session)

    async def get_by_id(self, post_id: int) -> Post:
        return await self.post_repo.get_post_by_id(post_id)

    async def get_all(self, offset: int = 0, limit: int = 20) -> List[Post]:
        return await self.post_repo.get_all_posts(offset, limit)

    async def create_post(self, post_data: dict) -> Post:
        return await self.post_repo.create_post(post_data.dict())

    async def delete_post(self, post_id: int) -> bool:
        return await self.post_repo.delete_post(post_id)

    async def update_post(self, post_id: int, post_data: dict) -> None | Post:
        update_data = {k: v for k, v in post_data.dict().items() if v is not None}
        return await self.post_repo.update_post(post_id, update_data)
