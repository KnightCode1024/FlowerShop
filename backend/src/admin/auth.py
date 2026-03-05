from sqlalchemy import select
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from entrypoint.ioc.engine import session_factory
from models import RoleEnum, User
from utils.jwt_utils import decode_jwt


class JWTAdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        super().__init__(secret_key=secret_key)

    async def _has_admin_access(self, request: Request) -> bool:
        access_token = request.cookies.get("access_token")
        if not access_token:
            return False

        try:
            payload = decode_jwt(access_token)
            user_id = int(payload.get("sub"))
        except Exception:
            return False

        if not user_id:
            return False

        async with session_factory() as session:
            result = await session.execute(
                select(User).where(User.id == user_id),
            )
            user = result.scalar_one_or_none()

        if not user:
            return False

        return user.role in {RoleEnum.ADMIN, RoleEnum.EMPLOYEE}

    async def login(self, request: Request) -> bool:
        return await self._has_admin_access(request)

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return await self._has_admin_access(request)
