from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from models.user import RoleEnum
from schemas.user import UserCreate, UserUpdate, UserCreateConsole


class IUserRepository(Protocol):
    async def create(
        self,
        user_data: UserCreate | UserCreateConsole,
    ) -> User: ...

    async def get(self, user_id: int) -> User: ...

    async def get_user_by_email_token(self, token: str) -> User | None: ...

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[User]: ...

    async def update(self, user_data: UserUpdate) -> User: ...

    async def get_user_by_email(self, email: str) -> User | None: ...

    async def set_is_verify_user(self, user: User) -> bool: ...

    async def set_otp_secret(self, user: User, otp_secret: str | None): ...

    async def get_otp_secret(self, user: User) -> str | None: ...


class UserRepository(IUserRepository):
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())

        if getattr(user, "role", None) is None:
            user.role = RoleEnum.USER

        self.session.add(user)
        await self.session.flush()
        return user

    async def get(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[User] | None:
        query = select(User).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, user_id: int, user_data: UserUpdate) -> User | None:
        user = await self.get(user_id)
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

    async def get_user_by_email_token(self, token: str) -> User | None:
        query = select(User).where(User.token == token)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def set_is_verify_user(self, user: User, token: str) -> User:
        user.email_verified = True
        self.session.add(user)
        return user

    async def set_otp_secret(self, user: User, otp_secret: str | None):
        user.otp_secret = otp_secret
        self.session.add(user)
        return user

    async def get_otp_secret(self, user: User) -> str | None:
        query = select(User.otp_secret).where(User.id == user.id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
