import re

from core.permissions import require_roles
from core.uow import UnitOfWork
from models import RoleEnum
from repositories import IUserRepository
from schemas.user import (
    RefreshToken,
    TokenPair,
    UserCreate,
    UserCreateConsole,
    UserLogin,
    UserResponse,
    UserUpdate,
    OTPCode,
    AccessToken,
)
from utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_jwt,
    hash_password,
    validate_password,
)
from utils.otp_utils import (
    verify_otp_code, 
    generate_otp_code, 
    generate_otp_secret,
)
from tasks.email import send_verify_email, send_otp_code


class UserService:
    def __init__(
        self,
        uow: UnitOfWork,
        user_repository: IUserRepository,
    ):
        self.uow = uow
        self.user_repository = user_repository

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        self._validate_password(user_data.password, RoleEnum.USER)

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

            await send_verify_email.kiq(
                to_email=user.email,
                token=user.token,
            )

            return UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                role=user.role,
            )

    async def check_code(self, user: UserResponse, otp_code: OTPCode):
        otp_secret = await self.user_repository.get_otp_secret(user)

        if not verify_otp_code(otp_code.otp_code, otp_secret):
            raise ValueError("Not valid code")
        
        # async with self.uow:
        #     await self.user_repository.set_otp_secret(user, None)

        tokens = TokenPair(
            access_token=create_access_token({"sub": str(user.id)}),
            refresh_token=create_refresh_token({"sub": str(user.id)}),
        )
        return tokens

    async def verify_email(self, token: str):
        user = await self.user_repository.get_user_by_email_token(token)
        if user is None:
            raise ValueError("User not found")
        async with self.uow:
            await self.user_repository.set_is_verify_user(user, token)
            return True
        
    async def resend_otp_code(self, user: UserResponse):
        otp_secret = await self.user_repository.get_otp_secret(user)
        
        if not otp_secret:
            otp_secret = generate_otp_secret()
            async with self.uow:
                await self.user_repository.set_otp_secret(user, otp_secret)

        otp_code = generate_otp_code(otp_secret)
        await send_otp_code.kiq(user.email, otp_code)
        return True

    async def login_user(self, user_data: UserLogin) -> AccessToken:
        user = await self.user_repository.get_user_by_email(user_data.email)
        if user is None or not validate_password(
            user_data.password,
            user.password,
        ):
            raise ValueError("Uncorrect login or password")
        if not user.email_verified:
            raise ValueError("Email not verify")

        otp_secret = generate_otp_secret()
        otp_code = generate_otp_code(otp_secret)

        async with self.uow:
            await self.user_repository.set_otp_secret(user, otp_secret)
        
        await send_otp_code.kiq(user.email, otp_code)

        token = AccessToken(
            access_token=create_access_token({"sub": str(user.id)}, 5),
        )
        return token

    @require_roles([RoleEnum.ADMIN])
    async def update_user(
        self,
        user_id: int,
        user_update: UserUpdate,
        user: UserResponse,
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

    @require_roles([RoleEnum.ADMIN, RoleEnum.EMPLOYEE])
    async def get_user(
        self,
        user_id: int,
        current_user,
    ) -> UserResponse:
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

    async def get_user_by_id(self, user_id: int):
        user = await self.user_repository.get(user_id)
        return user

    @require_roles([RoleEnum.ADMIN])
    async def get_all_users(
        self,
        user: UserResponse,
        offset: int = 0,
        limit: int = 20,
    ):
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

    async def create_user_for_console(
        self, user_data: UserCreateConsole
    ) -> UserResponse:
        try:
            user_role = RoleEnum(user_data.role.lower())
        except ValueError:
            raise ValueError(
                f"Invalid role '{user_data.role}'.",
                "Must be one of: user, employee, admin",
            )

        self._validate_password(user_data.password, user_role)

        existing_user = await self.user_repository.get_user_by_email(
            user_data.email,
        )
        if existing_user is not None:
            raise ValueError("User with this email already exists")

        async with self.uow:
            hashed_password = hash_password(user_data.password)
            user_create_data = UserCreateConsole(
                email=user_data.email,
                username=user_data.username,
                password=hashed_password,
                role=user_role,
            )
            user = await self.user_repository.create(user_create_data)
            return UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                role=user.role,
            )

    def _validate_password(self, password: str, role: RoleEnum) -> None:

        if role in [RoleEnum.ADMIN, RoleEnum.EMPLOYEE]:
            if len(password) < 12:
                raise ValueError(
                    "Password must be at least 12 characters long ",
                    "for admin/employee roles",
                )

            if not re.search(r"[A-Z]", password):
                raise ValueError(
                    "Password must contain at least one uppercase letter",
                )

            if not re.search(r"[0-9]", password):
                raise ValueError("Password must contain at least one digit")

            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValueError(
                    "Password must contain at least one special character",
                )

        elif role == RoleEnum.USER:
            if len(password) < 8:
                raise ValueError(
                    "Password must be at least 8 characters long for user role"
                )

            if not re.search(r"[A-Z]", password):
                raise ValueError(
                    "Password must contain at least one uppercase letter",
                )

            if not re.search(r"[0-9]", password):
                raise ValueError("Password must contain at least one digit")
