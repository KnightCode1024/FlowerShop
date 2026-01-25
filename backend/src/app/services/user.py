from app.core.uow import UnitOfWork
from app.repositories import UserRepositoryI
from app.utils.jwt_utils import (
    validate_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_jwt,
)
from app.schemas.user import (
    TokenPair,
    RefreshToken,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserLogin,
)


class UserService:
    def __init__(
        self,
        uow: UnitOfWork,
        user_repository: UserRepositoryI,
    ):
        self.uow = uow
        self.user_repository = user_repository

    async def register_user(self, user_data: UserCreate) -> TokenPair:
        existing_user = await self.user_repository.get_user_by_email(
            user_data.email,
        )
        if existing_user is not None:
            raise ValueError("Email already exist")

        async with self.uow:
            hashed_password = hash_password(user_data.password)
            user_create_data = UserCreate(
                email=user_data.email,
                username=user_data.username,
                password=hashed_password,
            )
            user = await self.user_repository.create(user_create_data)
            tokens = TokenPair(
                access_token=create_access_token({"sub": str(user.id)}),
                refresh_token=create_refresh_token({"sub": str(user.id)}),
            )
            return tokens

    async def login_user(self, user_data: UserLogin) -> TokenPair:
        user = await self.user_repository.get_user_by_email(user_data.email)
        if user is None or not validate_password(
            user_data.password,
            user.password,
        ):
            raise ValueError("Invalid credentials")
        tokens = TokenPair(
            access_token=create_access_token({"sub": str(user.id)}),
            refresh_token=create_refresh_token({"sub": str(user.id)}),
        )
        return tokens

    async def update_user(
        self,
        user_id: int,
        user_update: UserUpdate,
    ) -> UserResponse:
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password"] = hash_password(update_data["password"])

        updated = await self.user_repository.update(
            user_id,
            UserUpdate(**update_data),
        )
        if not updated:
            raise LookupError("User not found")
        return UserResponse(
            id=updated.id,
            email=updated.email,
            username=updated.username,
            role=updated.role,
        )

    async def get_user(self, user_id: int) -> UserResponse:
        user = await self.user_repository.get(user_id)
        if not user:
            raise ValueError("User not found")
        user_repsonse = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
        )
        return user_repsonse

    async def get_all_users(self, offset: int = 0, limit: int = 20):
        users = await self.user_repository.get_all(offset, limit)
        if not users:
            raise ValueError("Not a single user was found")
        return users

    async def refresh_token(
        self,
        payload: RefreshToken,
    ) -> TokenPair:
        try:
            payload = decode_jwt(payload.refresh_token)
            print(f"Payload = {payload}")
        except Exception as exc:
            raise ValueError("Invalid token") from exc
        user_id = int(payload.get("sub"))
        print(f"User id = {user_id}")
        if not user_id:
            raise ValueError("Invalid token payload")
        user = await self.user_repository.get(user_id)
        print(f"User = {user}")
        if not user:
            raise LookupError("User not found")
        return TokenPair(
            access_token=create_access_token({"sub": str(user.id)}),
            refresh_token=create_refresh_token({"sub": str(user.id)}),
        )

    async def verify_token(self, token: str) -> UserResponse | None:
        try:
            payload = decode_jwt(token)
            user_id = int(payload.get("sub"))
            if not user_id:
                return None
            user = await self.user_repository.get(user_id)
            if not user:
                return None

            return UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                role=user.role,
            )
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
