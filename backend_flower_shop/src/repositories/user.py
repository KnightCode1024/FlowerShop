from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas.user import UserCreate, UserUpdate
from models import User


class UserRepositoryI(Protocol):
    async def create(self, user_data: UserCreate) -> User: ...

    async def get(self, user_id: int) -> User: ...

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[User]: ...

    async def update(self, user_data: UserUpdate) -> User: ...

    async def get_user_by_email(self, email: str) -> User | None: ...


class UserRepository(UserRepositoryI):
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        self.session.add(user)
        await self.session.flush()
        return user

    async def get(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[User] | None:
        query = select(User).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, user_id: int, user_data: UserUpdate) -> User | None:
        user = self.get(user_id)
        if not user:
            return None
        updated_data = user_data.model_dump(exclude_unset=True)
        for field, value in updated_data.items():
            setattr(user, field, value)
        self.session.add(user)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
